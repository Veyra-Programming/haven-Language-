"""
SSE parser and streaming chunk iterator with automatic Chain-of-Thought (<think>) extraction.
"""

from typing import Iterator, AsyncIterator, Optional, Dict, Any, Tuple
import json
from .models import StreamChunk, StreamChoice, StreamDelta


class ReasoningExtractor:
    """
    Streaming parser that separates reasoning traces (<think>...</think>)
    from the final response content in real time.
    """
    def __init__(self) -> None:
        self.in_think: bool = False
        self.buffer: str = ""
        self.accumulated_reasoning: str = ""
        self.accumulated_content: str = ""

    def process_chunk(self, raw_text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Process a text delta and return (content, reasoning_content).
        """
        if not raw_text:
            return None, None

        self.buffer += raw_text
        reasoning_delta: Optional[str] = None
        content_delta: Optional[str] = None

        while self.buffer:
            if not self.in_think:
                if "<think>" in self.buffer:
                    before, _, after = self.buffer.partition("<think>")
                    if before:
                        content_delta = (content_delta or "") + before
                        self.accumulated_content += before
                    self.in_think = True
                    self.buffer = after
                else:
                    # No <think> tag, emit content
                    content_delta = (content_delta or "") + self.buffer
                    self.accumulated_content += self.buffer
                    self.buffer = ""
            else:
                if "</think>" in self.buffer:
                    thought, _, after = self.buffer.partition("</think>")
                    if thought:
                        reasoning_delta = (reasoning_delta or "") + thought
                        self.accumulated_reasoning += thought
                    self.in_think = False
                    self.buffer = after
                else:
                    # Still inside <think>
                    reasoning_delta = (reasoning_delta or "") + self.buffer
                    self.accumulated_reasoning += self.buffer
                    self.buffer = ""

        return content_delta, reasoning_delta


class ChatStreamIterator:
    """Synchronous SSE iterator for streaming completions."""
    def __init__(self, raw_stream: Iterator[str]) -> None:
        self._raw_stream = raw_stream
        self._extractor = ReasoningExtractor()

    def __iter__(self) -> "ChatStreamIterator":
        return self

    def __next__(self) -> StreamChunk:
        for line in self._raw_stream:
            line = line.strip()
            if not line or line.startswith(":"):
                continue
            if line.startswith("data: "):
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    chunk_id = data.get("id", "stream-chunk")
                    model = data.get("model", "")
                    choices_data = data.get("choices", [])
                    choices = []
                    for c in choices_data:
                        delta_dict = c.get("delta", {})
                        raw_content = delta_dict.get("content", "")
                        role = delta_dict.get("role")
                        finish = c.get("finish_reason")

                        # If model supplies dedicated reasoning_content, use it; otherwise extract from tags
                        explicit_reasoning = delta_dict.get("reasoning_content")
                        if explicit_reasoning is not None:
                            content_val = raw_content
                            reasoning_val = explicit_reasoning
                        else:
                            content_val, reasoning_val = self._extractor.process_chunk(raw_content)

                        delta = StreamDelta(
                            role=role,
                            content=content_val,
                            reasoning_content=reasoning_val
                        )
                        choices.append(StreamChoice(index=c.get("index", 0), delta=delta, finish_reason=finish))

                    return StreamChunk(id=chunk_id, model=model, choices=choices)
                except Exception:
                    continue

        raise StopIteration

    @property
    def full_content(self) -> str:
        return self._extractor.accumulated_content

    @property
    def full_reasoning(self) -> str:
        return self._extractor.accumulated_reasoning


class AsyncChatStreamIterator:
    """Asynchronous SSE iterator for streaming completions."""
    def __init__(self, raw_stream: AsyncIterator[str]) -> None:
        self._raw_stream = raw_stream
        self._extractor = ReasoningExtractor()

    def __aiter__(self) -> "AsyncChatStreamIterator":
        return self

    async def __anext__(self) -> StreamChunk:
        async for line in self._raw_stream:
            line = line.strip()
            if not line or line.startswith(":"):
                continue
            if line.startswith("data: "):
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                    chunk_id = data.get("id", "stream-chunk")
                    model = data.get("model", "")
                    choices_data = data.get("choices", [])
                    choices = []
                    for c in choices_data:
                        delta_dict = c.get("delta", {})
                        raw_content = delta_dict.get("content", "")
                        role = delta_dict.get("role")
                        finish = c.get("finish_reason")

                        explicit_reasoning = delta_dict.get("reasoning_content")
                        if explicit_reasoning is not None:
                            content_val = raw_content
                            reasoning_val = explicit_reasoning
                        else:
                            content_val, reasoning_val = self._extractor.process_chunk(raw_content)

                        delta = StreamDelta(
                            role=role,
                            content=content_val,
                            reasoning_content=reasoning_val
                        )
                        choices.append(StreamChoice(index=c.get("index", 0), delta=delta, finish_reason=finish))

                    return StreamChunk(id=chunk_id, model=model, choices=choices)
                except Exception:
                    continue

        raise StopAsyncIteration

    @property
    def full_content(self) -> str:
        return self._extractor.accumulated_content

    @property
    def full_reasoning(self) -> str:
        return self._extractor.accumulated_reasoning
