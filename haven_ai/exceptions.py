"""
Typed exception hierarchy for Haven AI SDK.
"""

from typing import Optional, Any, Dict


class HavenAIError(Exception):
    """Base exception for all Haven AI SDK errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AuthenticationError(HavenAIError):
    """Raised when authentication fails (HTTP 401)."""
    def __init__(self, message: str = "Invalid or missing Hugging Face API token.") -> None:
        super().__init__(message, status_code=401)


class RateLimitError(HavenAIError):
    """Raised when API rate limit is exceeded (HTTP 429)."""
    def __init__(self, message: str, retry_after: Optional[float] = None) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ModelLoadingError(HavenAIError):
    """Raised when model is loading / cold start (HTTP 503)."""
    def __init__(self, message: str, estimated_time: Optional[float] = None) -> None:
        super().__init__(message, status_code=503)
        self.estimated_time = estimated_time


class ProviderError(HavenAIError):
    """Raised when an inference provider fails or cannot fulfill the request."""
    def __init__(self, message: str, provider: Optional[str] = None, status_code: Optional[int] = None) -> None:
        super().__init__(message, status_code=status_code)
        self.provider = provider


class InferenceTimeoutError(HavenAIError):
    """Raised when an inference request times out."""
    pass


class InvalidRequestError(HavenAIError):
    """Raised when the request parameters or schema are invalid (HTTP 400)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, status_code=400, payload=details)
        self.details = details or {}
