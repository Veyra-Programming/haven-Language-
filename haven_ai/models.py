"""
Data models for Haven AI requests and responses.
Supports Pydantic v2 with a seamless dataclass fallback for zero-dependency environments.
"""

from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import json

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    from dataclasses import dataclass, field, asdict

if HAS_PYDANTIC:
    class BaseSchema(BaseModel):
        """Base schema with dict-like compatibility."""
        model_config = {"arbitrary_types_allowed": True}

        def to_dict(self) -> Dict[str, Any]:
            return self.model_dump()

    class ChatMessage(BaseSchema):
        role: str
        content: str
        name: Optional[str] = None

    class UsageInfo(BaseSchema):
        prompt_tokens: int = 0
        completion_tokens: int = 0
        total_tokens: int = 0

    class ChatChoice(BaseSchema):
        index: int = 0
        message: ChatMessage
        finish_reason: Optional[str] = None

    class ChatCompletionResponse(BaseSchema):
        id: str
        model: str
        choices: List[ChatChoice]
        usage: UsageInfo = Field(default_factory=UsageInfo)
        reasoning_content: Optional[str] = None

        @property
        def content(self) -> str:
            if self.choices and self.choices[0].message:
                return self.choices[0].message.content
            return ""

    class StreamDelta(BaseSchema):
        role: Optional[str] = None
        content: Optional[str] = None
        reasoning_content: Optional[str] = None

    class StreamChoice(BaseSchema):
        index: int = 0
        delta: StreamDelta
        finish_reason: Optional[str] = None

    class StreamChunk(BaseSchema):
        id: str
        model: str
        choices: List[StreamChoice]

        @property
        def content(self) -> str:
            if self.choices and self.choices[0].delta and self.choices[0].delta.content:
                return self.choices[0].delta.content
            return ""

        @property
        def reasoning(self) -> str:
            if self.choices and self.choices[0].delta and self.choices[0].delta.reasoning_content:
                return self.choices[0].delta.reasoning_content
            return ""

    class EmbeddingResponse(BaseSchema):
        model: str
        embeddings: List[List[float]]
        usage: UsageInfo = Field(default_factory=UsageInfo)

else:
    class BaseSchema:
        def to_dict(self) -> Dict[str, Any]:
            return asdict(self)  # type: ignore

        def model_dump(self) -> Dict[str, Any]:
            return self.to_dict()

        def model_dump_json(self) -> str:
            return json.dumps(self.to_dict())

    @dataclass
    class ChatMessage(BaseSchema):
        role: str
        content: str
        name: Optional[str] = None

    @dataclass
    class UsageInfo(BaseSchema):
        prompt_tokens: int = 0
        completion_tokens: int = 0
        total_tokens: int = 0

    @dataclass
    class ChatChoice(BaseSchema):
        index: int = 0
        message: ChatMessage = field(default_factory=lambda: ChatMessage(role="assistant", content=""))
        finish_reason: Optional[str] = None

    @dataclass
    class ChatCompletionResponse(BaseSchema):
        id: str
        model: str
        choices: List[ChatChoice]
        usage: UsageInfo = field(default_factory=UsageInfo)
        reasoning_content: Optional[str] = None

        @property
        def content(self) -> str:
            if self.choices and self.choices[0].message:
                return self.choices[0].message.content
            return ""

    @dataclass
    class StreamDelta(BaseSchema):
        role: Optional[str] = None
        content: Optional[str] = None
        reasoning_content: Optional[str] = None

    @dataclass
    class StreamChoice(BaseSchema):
        index: int = 0
        delta: StreamDelta = field(default_factory=StreamDelta)
        finish_reason: Optional[str] = None

    @dataclass
    class StreamChunk(BaseSchema):
        id: str
        model: str
        choices: List[StreamChoice]

        @property
        def content(self) -> str:
            if self.choices and self.choices[0].delta and self.choices[0].delta.content:
                return self.choices[0].delta.content
            return ""

        @property
        def reasoning(self) -> str:
            if self.choices and self.choices[0].delta and self.choices[0].delta.reasoning_content:
                return self.choices[0].delta.reasoning_content
            return ""

    @dataclass
    class EmbeddingResponse(BaseSchema):
        model: str
        embeddings: List[List[float]]
        usage: UsageInfo = field(default_factory=UsageInfo)


class ImageResponse:
    """Wrapper for image generation responses supporting raw bytes and PIL saving."""
    def __init__(self, data: bytes, format: str = "png") -> None:
        self.data: bytes = data
        self.format: str = format

    def save(self, path: Union[str, Path]) -> str:
        """Save image bytes directly to a file."""
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(self.data)
        return str(target_path)

    def to_pil(self) -> Any:
        """Convert image bytes to a PIL Image instance if pillow is installed."""
        try:
            from PIL import Image  # type: ignore
            import io
            return Image.open(io.BytesIO(self.data))
        except ImportError as e:
            raise ImportError("Pillow is required to convert to PIL.Image. Install via 'pip install pillow'.") from e

    def __bytes__(self) -> bytes:
        return self.data

    def __repr__(self) -> str:
        return f"ImageResponse(bytes={len(self.data)}, format={self.format!r})"
