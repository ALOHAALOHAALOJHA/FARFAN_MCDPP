"""
Context Provider Factory - Support for Multiple Enrichment Domains

Enables pluggable context providers for different enrichment domains
beyond PDET (e.g., international contexts, cross-domain data).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentContext:
    """Generic enrichment context data."""

    context_type: str
    context_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "context_type": self.context_type,
            "context_id": self.context_id,
            "data": self.data,
            "metadata": self.metadata,
            "version": self.version,
        }


class ContextProviderProtocol(Protocol):
    """Protocol for context providers."""

    @property
    def provider_name(self) -> str:
        """Unique provider name."""
        ...

    @property
    def supported_contexts(self) -> List[str]:
        """List of context types this provider supports."""
        ...

    def load_context(
        self, context_type: str, filters: Optional[Dict[str, Any]] = None
    ) -> EnrichmentContext:
        """Load enrichment context."""
        ...

    def validate_context(self, context: EnrichmentContext) -> bool:
        """Validate context data integrity."""
        ...


class BaseContextProvider(ABC):
    """Base class for context providers."""

    def __init__(
        self, provider_name: str, data_path: Optional[Path] = None, cache_enabled: bool = True
    ):
        self._provider_name = provider_name
        self._data_path = data_path
        self._cache_enabled = cache_enabled
        self._cache: Dict[str, EnrichmentContext] = {}

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    @abstractmethod
    def supported_contexts(self) -> List[str]:
        """Return list of supported context types."""
        pass

    @abstractmethod
    def _load_raw_data(self, context_type: str) -> Dict[str, Any]:
        """Load raw data from source."""
        pass

    @abstractmethod
    def _filter_data(
        self, raw_data: Dict[str, Any], filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply filters to raw data."""
        pass

    def load_context(
        self, context_type: str, filters: Optional[Dict[str, Any]] = None
    ) -> EnrichmentContext:
        """
        Load enrichment context with optional filtering.

        Args:
            context_type: Type of context to load
            filters: Optional filters to apply

        Returns:
            EnrichmentContext object
        """
        if context_type not in self.supported_contexts:
            raise ValueError(f"Context type '{context_type}' not supported by {self.provider_name}")

        # Check cache
        cache_key = f"{context_type}:{json.dumps(filters or {}, sort_keys=True)}"
        if self._cache_enabled and cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]

        # Load and filter data
        raw_data = self._load_raw_data(context_type)
        filtered_data = self._filter_data(raw_data, filters)

        context = EnrichmentContext(
            context_type=context_type,
            context_id=f"{self.provider_name}:{context_type}",
            data=filtered_data,
            metadata={
                "provider": self.provider_name,
                "filters_applied": filters or {},
                "data_source": str(self._data_path) if self._data_path else "unknown",
            },
        )

        # Cache result
        if self._cache_enabled:
            self._cache[cache_key] = context

        return context

    def validate_context(self, context: EnrichmentContext) -> bool:
        """Validate context data."""
        if not context.data:
            return False
        if context.context_type not in self.supported_contexts:
            return False
        return True

    def clear_cache(self) -> None:
        """Clear the context cache."""
        self._cache.clear()


class PDETContextProvider(BaseContextProvider):
    """Context provider for PDET municipalities data."""

    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            data_path = (
                Path(__file__).resolve().parent.parent
                / "colombia_context"
                / "pdet_municipalities.json"
            )

        super().__init__(provider_name="PDET_Colombia", data_path=data_path, cache_enabled=True)
        self._pdet_data: Optional[Dict[str, Any]] = None

    @property
    def supported_contexts(self) -> List[str]:
        return [
            "municipalities",
            "subregions",
            "policy_areas",
            "pillars",
            "statistics",
            "governance",
        ]

    def _load_raw_data(self, context_type: str) -> Dict[str, Any]:
        """Load PDET data from JSON file."""
        if self._pdet_data is None:
            with open(self._data_path, "r", encoding="utf-8") as f:
                self._pdet_data = json.load(f)

        return self._pdet_data

    def _filter_data(
        self, raw_data: Dict[str, Any], filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Filter PDET data based on criteria."""
        if not filters:
            return self._extract_context_data(raw_data, "all")

        policy_areas = filters.get("policy_areas", [])
        if policy_areas:
            return self._filter_by_policy_areas(raw_data, policy_areas)

        return self._extract_context_data(raw_data, "all")

    def _extract_context_data(self, raw_data: Dict[str, Any], context_type: str) -> Dict[str, Any]:
        """Extract specific context from raw data."""
        if context_type == "municipalities":
            return {"municipalities": self._get_all_municipalities(raw_data)}
        elif context_type == "subregions":
            return {"subregions": raw_data.get("subregions", [])}
        elif context_type == "all":
            return raw_data
        else:
            return {context_type: raw_data.get(context_type, {})}

    def _get_all_municipalities(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all municipalities from subregions."""
        municipalities = []
        for subregion in raw_data.get("subregions", []):
            municipalities.extend(subregion.get("municipalities", []))
        return municipalities

    def _filter_by_policy_areas(
        self, raw_data: Dict[str, Any], policy_areas: List[str]
    ) -> Dict[str, Any]:
        """Filter data by policy areas."""
        pa_mappings = raw_data.get("policy_area_mappings", {})

        relevant_subregion_ids = set()
        for pa in policy_areas:
            pa_key = f"{pa}" if pa.startswith("PA") else f"PA{pa}"

            # Try exact match first, then prefix match
            pa_data = pa_mappings.get(pa_key)
            if not pa_data:
                # Try to find by prefix (e.g., PA01 matches PA01_Gender)
                for key, value in pa_mappings.items():
                    if key.startswith(pa_key + "_") or key == pa_key:
                        pa_data = value
                        break

            if pa_data:
                relevant_subregion_ids.update(pa_data.get("relevant_subregions", []))

        # Filter subregions
        filtered_subregions = [
            sr
            for sr in raw_data.get("subregions", [])
            if sr["subregion_id"] in relevant_subregion_ids
        ]

        return {
            "subregions": filtered_subregions,
            "policy_area_mappings": {
                k: v
                for k, v in pa_mappings.items()
                if any(pa in k or k.startswith(pa + "_") for pa in policy_areas)
            },
        }


class ContextProviderFactory:
    """Factory for creating and managing context providers."""

    def __init__(self):
        self._providers: Dict[str, ContextProviderProtocol] = {}
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        """Register default built-in providers."""
        self.register(PDETContextProvider())

    def register(self, provider: ContextProviderProtocol) -> None:
        """Register a context provider."""
        name = provider.provider_name
        if name in self._providers:
            logger.warning(f"Provider {name} already registered, overwriting")
        self._providers[name] = provider

    def unregister(self, provider_name: str) -> None:
        """Unregister a provider."""
        if provider_name in self._providers:
            del self._providers[provider_name]

    def get(self, provider_name: str) -> Optional[ContextProviderProtocol]:
        """Get a provider by name."""
        return self._providers.get(provider_name)

    def get_all(self) -> List[ContextProviderProtocol]:
        """Get all registered providers."""
        return list(self._providers.values())

    def get_provider_for_context(self, context_type: str) -> Optional[ContextProviderProtocol]:
        """Find a provider that supports the given context type."""
        for provider in self._providers.values():
            if context_type in provider.supported_contexts:
                return provider
        return None

    def load_context(
        self,
        context_type: str,
        provider_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> EnrichmentContext:
        """
        Load context using appropriate provider.

        Args:
            context_type: Type of context to load
            provider_name: Optional specific provider to use
            filters: Optional filters to apply

        Returns:
            EnrichmentContext object
        """
        if provider_name:
            provider = self.get(provider_name)
            if not provider:
                raise ValueError(f"Provider '{provider_name}' not found")
        else:
            provider = self.get_provider_for_context(context_type)
            if not provider:
                raise ValueError(f"No provider found for context type '{context_type}'")

        return provider.load_context(context_type, filters)

    def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered providers with their capabilities."""
        return [
            {"name": p.provider_name, "supported_contexts": p.supported_contexts}
            for p in self._providers.values()
        ]


# Global factory instance
_factory: Optional[ContextProviderFactory] = None


def get_context_factory() -> ContextProviderFactory:
    """Get or create the global context factory."""
    global _factory
    if _factory is None:
        _factory = ContextProviderFactory()
    return _factory
