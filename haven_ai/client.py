"""
Synchronous Haven AI Client for Hugging Face Inference Providers.
Includes zero-dependency fallback (urllib) and automatic httpx optimization.
"""

from typing import Optional, List, Dict, Any, Union, Iterator
import os
import time
import json
import urllib.request
import urllib.error

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .models import (
    ChatMessage,
    ChatCompletionResponse,
    ChatChoice,
    UsageInfo,
    ImageResponse,
    EmbeddingResponse,
)
from .providers import ProviderConfig, ProviderPolicy
from .streaming import ChatStreamIterator
from .exceptions import (
    HavenAIError,
    AuthenticationError,
    RateLimitError,
    ModelLoadingError,
    ProviderError,
    InferenceTimeoutError,
    InvalidRequestError,
)
from .pipeline_adapter import Pipeable, pipe_fn


class Client(Pipeable):
    """
    Main Synchronous Client for Hugging Face Inference Providers.
    Inherits from Pipeable to allow direct pipeline dispatch:
       "Hello Haven" |> client |> print
    """

    DEFAULT_CHAT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
    DEFAULT_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
    DEFAULT_EMBED_MODEL = "BAAI/bge-m3"

    def __init__(
        self,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        provider: Optional[str] = None,
        policy: Optional[Union[ProviderPolicy, str]] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        prefer_httpx: bool = True,
    ) -> None:
        resolved_key = api_key or token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        self.api_key: Optional[str] = resolved_key
        self.max_retries: int = max_retries
        self.timeout: float = timeout
        self.use_httpx: bool = HAS_HTTPX and prefer_httpx

        if isinstance(policy, str):
            policy = ProviderPolicy(policy)

        self.provider_config = ProviderConfig(
            provider=provider,
            policy=policy,
            custom_base_url=base_url
        )
        self.base_url: str = base_url or self.provider_config.ROUTER_URL

        # Initialize Pipeable base with self.chat as default target
        super().__init__(self.chat)

    def _get_auth_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "haven-ai-sdk/0.1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request_http(
        self,
        url: str,
        method: str = "POST",
        json_data: Optional[Dict[str, Any]] = None,
        raw_body: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ) -> Any:
        """Execute request with retries, backoff, and provider failover."""
        all_headers = self._get_auth_headers()
        if headers:
            all_headers.update(headers)

        payload_bytes: Optional[bytes] = None
        if json_data is not None:
            payload_bytes = json.dumps(json_data).encode("utf-8")
        elif raw_body is not None:
            payload_bytes = raw_body

        if self.use_httpx:
            return self._request_httpx(url, method, payload_bytes, all_headers, stream)
        else:
            return self._request_urllib(url, method, payload_bytes, all_headers, stream)

    def _request_httpx(
        self,
        url: str,
        method: str,
        payload_bytes: Optional[bytes],
        headers: Dict[str, str],
        stream: bool,
    ) -> Any:
        retries = 0
        while True:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    req = client.build_request(
                        method=method,
                        url=url,
                        content=payload_bytes,
                        headers=headers,
                    )
                    resp = client.send(req, stream=stream)

                    if resp.status_code == 401:
                        raise AuthenticationError("Invalid or missing HF_TOKEN.")
                    if resp.status_code == 429:
                        retry_after = float(resp.headers.get("retry-after", "2.0"))
                        if retries < self.max_retries:
                            time.sleep(retry_after)
                            retries += 1
                            continue
                        raise RateLimitError("Rate limit exceeded.", retry_after=retry_after)
                    if resp.status_code == 503:
                        try:
                            err_data = resp.json()
                            est_time = float(err_data.get("estimated_time", 5.0))
                        except Exception:
                            est_time = 5.0
                        if retries < self.max_retries:
                            time.sleep(min(est_time, 20.0))
                            retries += 1
                            continue
                        raise ModelLoadingError("Model currently loading.", estimated_time=est_time)
                    if resp.status_code >= 400:
                        raise HavenAIError(f"HTTP {resp.status_code}: {resp.text}", status_code=resp.status_code)

                    if stream:
                        return resp.iter_lines()
                    return resp.content
            except (httpx.TimeoutException, TimeoutError) as e:
                if retries < self.max_retries:
                    time.sleep(1.5 * (retries + 1))
                    retries += 1
                    continue
                raise InferenceTimeoutError(f"Request to {url} timed out.") from e

    def _request_urllib(
        self,
        url: str,
        method: str,
        payload_bytes: Optional[bytes],
        headers: Dict[str, str],
        stream: bool,
    ) -> Any:
        retries = 0
        while True:
            try:
                req = urllib.request.Request(url, data=payload_bytes, headers=headers, method=method)
                resp = urllib.request.urlopen(req, timeout=self.timeout)

                if stream:
                    def line_generator() -> Iterator[str]:
                        while True:
                            line = resp.readline()
                            if not line:
                                break
                            yield line.decode("utf-8")
                    return line_generator()

                return resp.read()
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                if e.code == 401:
                    raise AuthenticationError("Invalid or missing HF_TOKEN.") from e
                if e.code == 429:
                    retry_after = float(e.headers.get("retry-after", "2.0"))
                    if retries < self.max_retries:
                        time.sleep(retry_after)
                        retries += 1
                        continue
                    raise RateLimitError("Rate limit exceeded.", retry_after=retry_after) from e
                if e.code == 503:
                    try:
                        err_data = json.loads(body)
                        est_time = float(err_data.get("estimated_time", 5.0))
                    except Exception:
                        est_time = 5.0
                    if retries < self.max_retries:
                        time.sleep(min(est_time, 20.0))
                        retries += 1
                        continue
                    raise ModelLoadingError("Model currently loading.", estimated_time=est_time) from e
                if e.code >= 400:
                    raise HavenAIError(f"HTTP {e.code}: {body}", status_code=e.code) from e
            except (TimeoutError, urllib.error.URLError) as e:
                if retries < self.max_retries:
                    time.sleep(1.5 * (retries + 1))
                    retries += 1
                    continue
                raise InferenceTimeoutError(f"Network request to {url} failed: {e}") from e

    def chat(
        self,
        messages: Union[str, List[Dict[str, str]], List[ChatMessage]],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        provider: Optional[str] = None,
        **extra_kwargs: Any
    ) -> Union[ChatCompletionResponse, ChatStreamIterator]:
        """
        OpenAI-compatible chat completion endpoint.
        Accepts both structured messages or raw prompt strings for convenient pipeline usage.
        """
        # Normalize messages
        formatted_messages: List[Dict[str, Any]] = []
        if isinstance(messages, str):
            formatted_messages = [{"role": "user", "content": messages}]
        else:
            for m in messages:
                if hasattr(m, "model_dump"):
                    formatted_messages.append(m.model_dump())
                elif isinstance(m, dict):
                    formatted_messages.append(m)
                else:
                    formatted_messages.append({"role": getattr(m, "role", "user"), "content": getattr(m, "content", str(m))})

        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            **extra_kwargs
        }

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        providers_to_try = [provider] if provider else self.provider_config.get_provider_chain()
        last_error: Optional[Exception] = None

        for p_target in providers_to_try:
            headers = self.provider_config.get_headers(p_target)
            try:
                raw_result = self._request_http(url, method="POST", json_data=payload, headers=headers, stream=stream)

                if stream:
                    return ChatStreamIterator(raw_result)

                data = json.loads(raw_result.decode("utf-8"))
                choices = []
                for c in data.get("choices", []):
                    msg_dict = c.get("message", {})
                    msg = ChatMessage(
                        role=msg_dict.get("role", "assistant"),
                        content=msg_dict.get("content", ""),
                    )
                    choices.append(ChatChoice(index=c.get("index", 0), message=msg, finish_reason=c.get("finish_reason")))

                usage_data = data.get("usage", {})
                usage = UsageInfo(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0),
                )

                # Extract top-level reasoning if present
                reasoning = None
                if choices and "<think>" in choices[0].message.content:
                    from .streaming import ReasoningExtractor
                    ext = ReasoningExtractor()
                    clean_content, extracted_reason = ext.process_chunk(choices[0].message.content)
                    choices[0].message.content = clean_content or ""
                    reasoning = extracted_reason

                return ChatCompletionResponse(
                    id=data.get("id", "chatcmpl-response"),
                    model=data.get("model", model),
                    choices=choices,
                    usage=usage,
                    reasoning_content=reasoning
                )
            except (RateLimitError, ModelLoadingError, AuthenticationError):
                raise
            except Exception as e:
                last_error = e
                continue

        raise ProviderError(f"All inference providers failed. Last error: {last_error}")

    def image(
        self,
        prompt: str,
        model: str = DEFAULT_IMAGE_MODEL,
        negative_prompt: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        **extra_params: Any
    ) -> ImageResponse:
        """Text-to-image generation returning an ImageResponse wrapper."""
        url = f"{self.provider_config.SERVERLESS_URL}/{model}"
        payload: Dict[str, Any] = {"inputs": prompt, "parameters": {**extra_params}}
        if negative_prompt:
            payload["parameters"]["negative_prompt"] = negative_prompt
        if height:
            payload["parameters"]["height"] = height
        if width:
            payload["parameters"]["width"] = width

        raw_bytes = self._request_http(url, method="POST", json_data=payload)
        return ImageResponse(data=raw_bytes, format="png")

    def embed(
        self,
        texts: Union[str, List[str]],
        model: str = DEFAULT_EMBED_MODEL,
    ) -> EmbeddingResponse:
        """Generate text embeddings."""
        url = f"{self.provider_config.SERVERLESS_URL}/{model}"
        inputs = [texts] if isinstance(texts, str) else texts
        payload = {"inputs": inputs}

        raw_bytes = self._request_http(url, method="POST", json_data=payload)
        data = json.loads(raw_bytes.decode("utf-8"))

        if isinstance(data, list) and data and isinstance(data[0], list):
            embeddings = data
        elif isinstance(data, list) and data and isinstance(data[0], (int, float)):
            embeddings = [data]
        else:
            embeddings = []

        return EmbeddingResponse(model=model, embeddings=embeddings)

    def pipe(self, model: str = DEFAULT_CHAT_MODEL, **kwargs: Any) -> Pipeable:
        """Convenience method returning a functional pipeline adapter."""
        return pipe_fn(self, model=model, **kwargs)
