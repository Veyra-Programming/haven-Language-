"""
Asynchronous Haven AI Client for Hugging Face Inference Providers.
"""

from typing import Optional, List, Dict, Any, Union, AsyncIterator
import os
import asyncio
import json

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
from .streaming import AsyncChatStreamIterator
from .exceptions import (
    HavenAIError,
    AuthenticationError,
    RateLimitError,
    ModelLoadingError,
    ProviderError,
    InferenceTimeoutError,
)
from .client import Client


class AsyncClient:
    """Asynchronous Client for Hugging Face Inference Providers."""

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
    ) -> None:
        resolved_key = api_key or token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
        self.api_key: Optional[str] = resolved_key
        self.max_retries: int = max_retries
        self.timeout: float = timeout

        if isinstance(policy, str):
            policy = ProviderPolicy(policy)

        self.provider_config = ProviderConfig(
            provider=provider,
            policy=policy,
            custom_base_url=base_url
        )
        self.base_url: str = base_url or self.provider_config.ROUTER_URL
        self._sync_fallback = Client(
            api_key=resolved_key,
            provider=provider,
            policy=policy,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
        )

    def _get_auth_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "haven-ai-sdk/0.1.0 (async)",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat(
        self,
        messages: Union[str, List[Dict[str, str]], List[ChatMessage]],
        model: str = DEFAULT_CHAT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        provider: Optional[str] = None,
        **extra_kwargs: Any
    ) -> Union[ChatCompletionResponse, AsyncChatStreamIterator]:
        """Async chat completions."""
        if not HAS_HTTPX:
            # Fallback to running synchronous client in background thread
            sync_res = await asyncio.to_thread(
                self._sync_fallback.chat,
                messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                provider=provider,
                **extra_kwargs
            )
            return sync_res

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
            headers = self._get_auth_headers()
            headers.update(self.provider_config.get_headers(p_target))

            retries = 0
            while True:
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        req = client.build_request("POST", url, json=payload, headers=headers)
                        resp = await client.send(req, stream=stream)

                        if resp.status_code == 401:
                            raise AuthenticationError("Invalid or missing HF_TOKEN.")
                        if resp.status_code == 429:
                            retry_after = float(resp.headers.get("retry-after", "2.0"))
                            if retries < self.max_retries:
                                await asyncio.sleep(retry_after)
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
                                await asyncio.sleep(min(est_time, 20.0))
                                retries += 1
                                continue
                            raise ModelLoadingError("Model currently loading.", estimated_time=est_time)
                        if resp.status_code >= 400:
                            raise HavenAIError(f"HTTP {resp.status_code}: {resp.text}", status_code=resp.status_code)

                        if stream:
                            return AsyncChatStreamIterator(resp.aiter_lines())

                        data = resp.json()
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

                        return ChatCompletionResponse(
                            id=data.get("id", "async-chatcmpl"),
                            model=data.get("model", model),
                            choices=choices,
                            usage=usage,
                        )
                except (RateLimitError, ModelLoadingError, AuthenticationError):
                    raise
                except Exception as e:
                    last_error = e
                    break  # Try next provider

        raise ProviderError(f"All async inference providers failed. Last error: {last_error}")

    async def image(self, prompt: str, model: str = DEFAULT_IMAGE_MODEL, **extra_params: Any) -> ImageResponse:
        """Async text-to-image generation."""
        return await asyncio.to_thread(self._sync_fallback.image, prompt, model=model, **extra_params)

    async def embed(self, texts: Union[str, List[str]], model: str = DEFAULT_EMBED_MODEL) -> EmbeddingResponse:
        """Async text embeddings."""
        return await asyncio.to_thread(self._sync_fallback.embed, texts, model=model)
