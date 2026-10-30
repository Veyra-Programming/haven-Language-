"""
Haven AI SDK - Lightweight Hugging Face Inference Providers Client with Native Pipeline Support.
"""

from .client import Client
from .async_client import AsyncClient
from .providers import ProviderConfig, ProviderPolicy, KnownProvider
from .models import (
    ChatMessage,
    ChatChoice,
    UsageInfo,
    ChatCompletionResponse,
    StreamDelta,
    StreamChoice,
    StreamChunk,
    ImageResponse,
    EmbeddingResponse,
)
from .streaming import ChatStreamIterator, AsyncChatStreamIterator, ReasoningExtractor
from .pipeline_adapter import Pipeable, pipe_fn
from .exceptions import (
    HavenAIError,
    AuthenticationError,
    RateLimitError,
    ModelLoadingError,
    ProviderError,
    InferenceTimeoutError,
    InvalidRequestError,
)

__version__ = "0.1.0"

__all__ = [
    # Clients
    "Client",
    "AsyncClient",
    # Providers
    "ProviderConfig",
    "ProviderPolicy",
    "KnownProvider",
    # Models
    "ChatMessage",
    "ChatChoice",
    "UsageInfo",
    "ChatCompletionResponse",
    "StreamDelta",
    "StreamChoice",
    "StreamChunk",
    "ImageResponse",
    "EmbeddingResponse",
    # Streaming
    "ChatStreamIterator",
    "AsyncChatStreamIterator",
    "ReasoningExtractor",
    # Pipeline & Custom Runtime
    "Pipeable",
    "pipe_fn",
    # Exceptions
    "HavenAIError",
    "AuthenticationError",
    "RateLimitError",
    "ModelLoadingError",
    "ProviderError",
    "InferenceTimeoutError",
    "InvalidRequestError",
]
