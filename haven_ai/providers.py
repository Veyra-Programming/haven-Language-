"""
Hugging Face Inference Providers and Router Configuration.
"""

from typing import List, Optional, Dict
from enum import Enum


class ProviderPolicy(str, Enum):
    FASTEST = ":fastest"
    CHEAPEST = ":cheapest"
    PREFERRED = ":preferred"
    DEFAULT = "auto"


class KnownProvider(str, Enum):
    TOGETHER = "together"
    NOVITA = "novita"
    FAL_AI = "fal-ai"
    GROQ = "groq"
    HF_INFERENCE = "hf-inference"
    HYPERBOLIC = "hyperbolic"
    FIREWORKS = "fireworks-ai"
    SAMBANOVA = "sambanova"


class ProviderConfig:
    """Configuration for Hugging Face Router & Serverless Inference."""

    ROUTER_URL: str = "https://router.huggingface.co/v1"
    SERVERLESS_URL: str = "https://api-inference.huggingface.co/models"

    DEFAULT_FALLBACKS: List[str] = [
        KnownProvider.HF_INFERENCE.value,
        KnownProvider.TOGETHER.value,
        KnownProvider.NOVITA.value,
        KnownProvider.GROQ.value,
    ]

    def __init__(
        self,
        provider: Optional[str] = None,
        policy: Optional[ProviderPolicy] = None,
        fallback_providers: Optional[List[str]] = None,
        custom_base_url: Optional[str] = None,
    ) -> None:
        self.provider: Optional[str] = provider
        self.policy: ProviderPolicy = policy or ProviderPolicy.DEFAULT
        self.fallback_providers: List[str] = (
            fallback_providers if fallback_providers is not None else list(self.DEFAULT_FALLBACKS)
        )
        self.custom_base_url: Optional[str] = custom_base_url

    def get_headers(self, current_provider: Optional[str] = None) -> Dict[str, str]:
        """Generate provider-specific HTTP headers."""
        headers: Dict[str, str] = {}
        target = current_provider or self.provider

        if target:
            headers["X-HF-Provider"] = target
        elif self.policy != ProviderPolicy.DEFAULT:
            headers["X-HF-Provider-Policy"] = self.policy.value

        return headers

    def get_provider_chain(self) -> List[Optional[str]]:
        """Return the prioritized failover sequence of providers."""
        chain: List[Optional[str]] = []
        if self.provider:
            chain.append(self.provider)
        for fb in self.fallback_providers:
            if fb not in chain:
                chain.append(fb)
        if not chain:
            chain.append(None)  # None denotes auto / router default
        return chain
