"""
Colombia Context Module
========================

This module provides Colombia-specific context for FARFAN questionnaire analysis.

The context includes:
- Territorial organization (departments, municipalities, special regions)
- Legal framework (constitution, laws, treaties)
- Institutional framework (ministries, special entities)
- Development plans (PND, sectoral plans)
- Key statistics (violence, gender, environment, migration)
- Territorial context (regions and their specific issues)
- Peace Agreement context

Usage:
------
    from canonic_questionnaire_central.colombia_context import (
        get_country_info,
        get_laws_for_policy_area,
        get_territorial_region_issues,
        get_key_statistics,
    )

    # Get country information
    info = get_country_info()

    # Get relevant laws for a policy area
    pa01_laws = get_laws_for_policy_area("PA01")

    # Get territorial context
    pacific_issues = get_territorial_region_issues("pacific_region")

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Path to Colombia context configuration
_COLOMBIA_CONTEXT_DIR = Path(__file__).parent
_CONTEXT_FILE = _COLOMBIA_CONTEXT_DIR / "colombia_context.json"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CountryInfo:
    """Basic country information."""
    name: str
    iso_code: str
    capital: str
    currency: str
    population: dict[str, Any]


@dataclass
class TerritorialOrganization:
    """Colombia's territorial organization."""
    departments: int
    districts: int
    municipalities: int
    indigenous_territories: int
    black_community_territories: int
    peasant_reserve_zones: int
    special_regions: list[dict[str, Any]]


@dataclass
class LegalFramework:
    """Legal framework including constitution, laws, and treaties."""
    constitution: dict[str, Any]
    key_laws: list[dict[str, Any]]
    international_treaties: list[dict[str, Any]]


@dataclass
class InstitutionalEntity:
    """An institutional entity."""
    entity_id: str
    name: str
    role: str | None = None
    pa: list[str] | None = None


@dataclass
class InstitutionalFramework:
    """Institutional framework."""
    executive_branch: dict[str, Any]
    special_entities: list[dict[str, Any]]


@dataclass
class DevelopmentPlan:
    """A development plan."""
    plan_id: str
    name: str
    period: str


@dataclass
class KeyStatistic:
    """A key statistic."""
    indicator: str
    value: float | int
    unit: str
    year: int
    source: str


# =============================================================================
# CONFIGURATION LOADER
# =============================================================================

class ColombiaContextLoader:
    """Loader for Colombia context configuration."""

    def __init__(self, json_path: Path | None = None):
        """Initialize loader.

        Args:
            json_path: Path to JSON file (uses default if None)
        """
        if json_path is None:
            json_path = _CONTEXT_FILE

        with open(json_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    def get_country_info(self) -> CountryInfo:
        """Get basic country information."""
        data = self._data.get("country", {})
        return CountryInfo(**data)

    def get_territorial_organization(self) -> TerritorialOrganization:
        """Get territorial organization."""
        data = self._data.get("territorial_organization", {})
        return TerritorialOrganization(
            departments=data.get("departments", 32),
            districts=data.get("districts", 1),
            municipalities=data.get("municipalities", 1119),
            indigenous_territories=data.get("indigenous_territories", 184),
            black_community_territories=data.get("black_community_territories", 167),
            peasant_reserve_zones=data.get("peasant_reserve_zones", 7),
            special_regions=data.get("special_regions", [])
        )

    def get_legal_framework(self) -> LegalFramework:
        """Get legal framework."""
        data = self._data.get("legal_framework", {})
        return LegalFramework(
            constitution=data.get("constitution", {}),
            key_laws=data.get("key_laws", []),
            international_treaties=data.get("international_treaties", [])
        )

    def get_institutional_framework(self) -> InstitutionalFramework:
        """Get institutional framework."""
        data = self._data.get("institutional_framework", {})
        return InstitutionalFramework(
            executive_branch=data.get("executive_branch", {}),
            special_entities=data.get("special_entities", [])
        )

    def get_laws_for_policy_area(self, policy_area_id: str) -> list[dict[str, Any]]:
        """Get key laws relevant to a policy area.

        Args:
            policy_area_id: Policy area identifier (e.g., "PA01")

        Returns:
            List of relevant laws
        """
        legal_data = self._data.get("legal_framework", {})
        all_laws = legal_data.get("key_laws", [])

        return [
            law for law in all_laws
            if policy_area_id in law.get("relevance", [])
        ]

    def get_treaties_for_policy_area(self, policy_area_id: str) -> list[dict[str, Any]]:
        """Get international treaties relevant to a policy area.

        Args:
            policy_area_id: Policy area identifier

        Returns:
            List of relevant treaties
        """
        legal_data = self._data.get("legal_framework", {})
        all_treaties = legal_data.get("international_treaties", [])

        return [
            treaty for treaty in all_treaties
            if policy_area_id in treaty.get("relevance", [])
        ]

    def get_key_statistics(self) -> dict[str, dict[str, Any]]:
        """Get key statistics by category.

        Returns:
            Dict of statistics by category (violence, gender, environmental, migration)
        """
        return self._data.get("key_statistics", {})

    def get_statistics_by_category(self, category: str) -> dict[str, Any]:
        """Get statistics for a specific category.

        Args:
            category: Category name (violence_indicators, gender_indicators, etc.)

        Returns:
            Dict of statistics for the category
        """
        stats = self._data.get("key_statistics", {})
        return stats.get(category, {})

    def get_territorial_regions(self) -> dict[str, dict[str, Any]]:
        """Get all territorial regions and their contexts.

        Returns:
            Dict of territorial regions
        """
        return self._data.get("territorial_context", {})

    def get_territorial_region(self, region_id: str) -> dict[str, Any]:
        """Get a specific territorial region context.

        Args:
            region_id: Region identifier (pacific_region, caribbean_region, etc.)

        Returns:
            Dict with region context
        """
        regions = self.get_territorial_regions()
        return regions.get(region_id, {})

    def get_territorial_region_issues(self, region_id: str) -> list[str]:
        """Get key issues for a territorial region.

        Args:
            region_id: Region identifier

        Returns:
            List of key issues
        """
        region = self.get_territorial_region(region_id)
        return region.get("key_issues", [])

    def get_development_plan(self) -> dict[str, Any]:
        """Get national development plan information.

        Returns:
            Dict with PND information
        """
        plans = self._data.get("development_plans", {})
        return plans.get("national_development_plan", {})

    def get_sectoral_plans(self) -> list[dict[str, Any]]:
        """Get sectoral plans.

        Returns:
            List of sectoral plans
        """
        plans = self._data.get("development_plans", {})
        return plans.get("sectoral_plans", [])

    def get_peace_agreement_context(self) -> dict[str, Any]:
        """Get Peace Agreement context.

        Returns:
            Dict with Peace Agreement information
        """
        return self._data.get("peace_agreement_context", {})


# =============================================================================
# GLOBAL LOADER INSTANCE
# =============================================================================

_loader: ColombiaContextLoader | None = None


def _get_loader() -> ColombiaContextLoader:
    """Get or create global loader instance."""
    global _loader
    if _loader is None:
        _loader = ColombiaContextLoader()
    return _loader


# =============================================================================
# PUBLIC API
# =============================================================================

def get_country_info() -> CountryInfo:
    """Get basic country information."""
    return _get_loader().get_country_info()


def get_territorial_organization() -> TerritorialOrganization:
    """Get territorial organization."""
    return _get_loader().get_territorial_organization()


def get_legal_framework() -> LegalFramework:
    """Get legal framework."""
    return _get_loader().get_legal_framework()


def get_laws_for_policy_area(policy_area_id: str) -> list[dict[str, Any]]:
    """Get key laws relevant to a policy area."""
    return _get_loader().get_laws_for_policy_area(policy_area_id)


def get_treaties_for_policy_area(policy_area_id: str) -> list[dict[str, Any]]:
    """Get international treaties relevant to a policy area."""
    return _get_loader().get_treaties_for_policy_area(policy_area_id)


def get_institutional_framework() -> InstitutionalFramework:
    """Get institutional framework."""
    return _get_loader().get_institutional_framework()


def get_key_statistics() -> dict[str, dict[str, Any]]:
    """Get key statistics by category."""
    return _get_loader().get_key_statistics()


def get_statistics_by_category(category: str) -> dict[str, Any]:
    """Get statistics for a specific category."""
    return _get_loader().get_statistics_by_category(category)


def get_territorial_regions() -> dict[str, dict[str, Any]]:
    """Get all territorial regions and their contexts."""
    return _get_loader().get_territorial_regions()


def get_territorial_region(region_id: str) -> dict[str, Any]:
    """Get a specific territorial region context."""
    return _get_loader().get_territorial_region(region_id)


def get_territorial_region_issues(region_id: str) -> list[str]:
    """Get key issues for a territorial region."""
    return _get_loader().get_territorial_region_issues(region_id)


def get_development_plan() -> dict[str, Any]:
    """Get national development plan information."""
    return _get_loader().get_development_plan()


def get_sectoral_plans() -> list[dict[str, Any]]:
    """Get sectoral plans."""
    return _get_loader().get_sectoral_plans()


def get_peace_agreement_context() -> dict[str, Any]:
    """Get Peace Agreement context."""
    return _get_loader().get_peace_agreement_context()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data structures
    "CountryInfo",
    "TerritorialOrganization",
    "LegalFramework",
    "InstitutionalEntity",
    "InstitutionalFramework",
    "DevelopmentPlan",
    "KeyStatistic",
    "ColombiaContextLoader",
    # API functions
    "get_country_info",
    "get_territorial_organization",
    "get_legal_framework",
    "get_laws_for_policy_area",
    "get_treaties_for_policy_area",
    "get_institutional_framework",
    "get_key_statistics",
    "get_statistics_by_category",
    "get_territorial_regions",
    "get_territorial_region",
    "get_territorial_region_issues",
    "get_development_plan",
    "get_sectoral_plans",
    "get_peace_agreement_context",
]
