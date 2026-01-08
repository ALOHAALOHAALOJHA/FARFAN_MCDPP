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
- Municipal governance (PDET regime, financial ecosystem, categorization)

Usage:
------
    from canonic_questionnaire_central.colombia_context import (
        get_country_info,
        get_laws_for_policy_area,
        get_territorial_region_issues,
        get_key_statistics,
        get_municipal_governance,
        get_pdet_info,
    )

    # Get country information
    info = get_country_info()

    # Get relevant laws for a policy area
    pa01_laws = get_laws_for_policy_area("PA01")

    # Get territorial context
    pacific_issues = get_territorial_region_issues("pacific_region")

    # Get municipal governance context
    gov = get_municipal_governance()

    # Get PDET information
    pdet = get_pdet_info()

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Path to Colombia context configuration
_COLOMBIA_CONTEXT_DIR = Path(__file__).parent
_CONTEXT_FILE = _COLOMBIA_CONTEXT_DIR / "colombia_context.json"
_MUNICIPAL_GOVERNANCE_FILE = _COLOMBIA_CONTEXT_DIR / "municipal_governance.json"


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


@dataclass
class MunicipalCategory:
    """A municipal category based on population and ICLD."""
    category: str
    population_range: str
    icld_range: str
    description: str
    fiscal_autonomy: str


@dataclass
class SgpComponent:
    """A component of the Sistema General de Participaciones."""
    percentage: float
    uses: list[str]
    rigidity: str


@dataclass
class PdetPillar:
    """A pillar of the PDET (Programas de Desarrollo con Enfoque Territorial)."""
    pillar_id: str
    name: str
    focus: list[str]
    status: str | None = None


@dataclass
class PdetInfo:
    """PDET (Programas de Desarrollo con Enfoque Territorial) information."""
    full_name: str
    acronym: str
    legal_basis: str
    planning_horizon_years: int
    territorial_scope: dict[str, Any]
    pillars: list[PdetPillar]
    implementation_status: dict[str, Any]
    key_gaps: dict[str, Any]


@dataclass
class MunicipalGovernance:
    """Colombian municipal governance context."""
    constitutional_foundation: dict[str, Any]
    legal_framework: dict[str, Any]
    categorization: list[MunicipalCategory]
    competencies: dict[str, Any]
    financial_ecosystem: dict[str, Any]
    pdet_regime: PdetInfo


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

    def _get_municipal_governance_data(self) -> dict[str, Any]:
        """Get municipal governance data from JSON file.

        Returns:
            Dict with municipal governance information
        """
        with open(_MUNICIPAL_GOVERNANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_municipal_governance(self) -> MunicipalGovernance:
        """Get municipal governance context.

        Returns:
            MunicipalGovernance dataclass with comprehensive governance information
        """
        data = self._get_municipal_governance_data()

        # Parse municipal categories
        categories_data = data.get("municipal_categorization", {}).get("categories", [])
        categories = [
            MunicipalCategory(
                category=cat.get("category", ""),
                population_range=cat.get("population_range", ""),
                icld_range=cat.get("icld_range", ""),
                description=cat.get("description", ""),
                fiscal_autonomy=cat.get("fiscal_autonomy", "")
            )
            for cat in categories_data
        ]

        # Parse PDET pillars
        pdet_data = data.get("pdet_regime", {})
        pillars_data = pdet_data.get("eight_pillars", {})
        pillars = [
            PdetPillar(
                pillar_id=key,
                name=pillar_data.get("name", ""),
                focus=pillar_data.get("focus", []),
                status=pillar_data.get("status")
            )
            for key, pillar_data in pillars_data.items()
        ]

        # Build PDET info
        pdet_info = PdetInfo(
            full_name=pdet_data.get("full_name", ""),
            acronym=pdet_data.get("acronym", ""),
            legal_basis=pdet_data.get("legal_basis", ""),
            planning_horizon_years=pdet_data.get("planning_horizon", 0),
            territorial_scope=pdet_data.get("territorial_scope", {}),
            pillars=pillars,
            implementation_status=pdet_data.get("implementation_status_2024", {}),
            key_gaps=pdet_data.get("the_gap", {})
        )

        return MunicipalGovernance(
            constitutional_foundation=data.get("constitutional_foundation", {}),
            legal_framework=data.get("legal_framework", {}),
            categorization=categories,
            competencies=data.get("municipal_competencies", {}),
            financial_ecosystem=data.get("financial_ecosystem", {}),
            pdet_regime=pdet_info
        )

    def get_pdet_info(self) -> PdetInfo:
        """Get PDET (Programas de Desarrollo con Enfoque Territorial) information.

        Returns:
            PdetInfo dataclass with PDET details
        """
        governance = self.get_municipal_governance()
        return governance.pdet_regime

    def get_municipal_category(self, category_name: str) -> MunicipalCategory | None:
        """Get a specific municipal category.

        Args:
            category_name: Category name (e.g., "Special", "First", "Sixth")

        Returns:
            MunicipalCategory if found, None otherwise
        """
        governance = self.get_municipal_governance()
        for category in governance.categorization:
            if category.category.lower() == category_name.lower():
                return category
        return None

    def get_sgp_components(self) -> dict[str, SgpComponent]:
        """Get Sistema General de Participaciones (SGP) components.

        Returns:
            Dict of SGP components by name
        """
        data = self._get_municipal_governance_data()
        sgp_data = data.get("financial_ecosystem", {}).get("system_general_participations", {})
        structure = sgp_data.get("structure", {})

        return {
            name: SgpComponent(
                percentage=value.get("percentage", 0.0),
                uses=value.get("uses", []),
                rigidity=value.get("rigidity", "")
            )
            for name, value in structure.items()
        }

    def get_ocad_paz_approvals(self) -> dict[str, Any]:
        """Get OCAD Paz historical approval data.

        Returns:
            Dict with OCAD Paz approval information
        """
        data = self._get_municipal_governance_data()
        return data.get("financial_ecosystem", {}).get("system_general_royalties", {}).get("ocad_paz", {})

    def get_pdet_pillar(self, pillar_id: str) -> PdetPillar | None:
        """Get a specific PDET pillar.

        Args:
            pillar_id: Pillar identifier (e.g., "pillar_1", "pillar_2")

        Returns:
            PdetPillar if found, None otherwise
        """
        pdet_info = self.get_pdet_info()
        for pillar in pdet_info.pillars:
            if pillar.pillar_id == pillar_id:
                return pillar
        return None


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


def get_municipal_governance() -> MunicipalGovernance:
    """Get municipal governance context.

    Returns:
        MunicipalGovernance dataclass with comprehensive governance information
        including constitutional foundation, legal framework, categorization,
        competencies, financial ecosystem, and PDET regime.
    """
    return _get_loader().get_municipal_governance()


def get_pdet_info() -> PdetInfo:
    """Get PDET (Programas de Desarrollo con Enfoque Territorial) information.

    Returns:
        PdetInfo dataclass with PDET details including legal basis,
        planning horizon, territorial scope, pillars, and implementation status.
    """
    return _get_loader().get_pdet_info()


def get_municipal_category(category_name: str) -> MunicipalCategory | None:
    """Get a specific municipal category.

    Args:
        category_name: Category name (e.g., "Special", "First", "Sixth")

    Returns:
        MunicipalCategory if found, None otherwise
    """
    return _get_loader().get_municipal_category(category_name)


def get_sgp_components() -> dict[str, SgpComponent]:
    """Get Sistema General de Participaciones (SGP) components.

    Returns:
        Dict of SGP components by name (education, health, water_sanitation, etc.)
    """
    return _get_loader().get_sgp_components()


def get_ocad_paz_approvals() -> dict[str, Any]:
    """Get OCAD Paz historical approval data.

    Returns:
        Dict with OCAD Paz approval information including project counts
        and investment values.
    """
    return _get_loader().get_ocad_paz_approvals()


def get_pdet_pillar(pillar_id: str) -> PdetPillar | None:
    """Get a specific PDET pillar.

    Args:
        pillar_id: Pillar identifier (e.g., "pillar_1", "pillar_2")

    Returns:
        PdetPillar if found, None otherwise
    """
    return _get_loader().get_pdet_pillar(pillar_id)


# =============================================================================
# PDET MUNICIPALITIES LOADER
# =============================================================================

_PDET_MUNICIPALITIES_FILE = _COLOMBIA_CONTEXT_DIR / "pdet_municipalities.json"


def get_pdet_municipalities() -> dict[str, Any]:
    """Get PDET municipalities detailed context.
    
    Returns:
        Dict with PDET municipalities data including subregions, 
        policy area mappings, and aggregate statistics.
    """
    with open(_PDET_MUNICIPALITIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_pdet_subregions() -> list[dict[str, Any]]:
    """Get PDET subregions with municipalities.
    
    Returns:
        List of PDET subregions
    """
    pdet_data = get_pdet_municipalities()
    return pdet_data.get("subregions", [])


def get_pdet_municipalities_for_policy_area(policy_area_id: str) -> list[dict[str, Any]]:
    """Get PDET municipalities relevant to a policy area.
    
    Args:
        policy_area_id: Policy area identifier (e.g., "PA01")
        
    Returns:
        List of relevant municipalities
    """
    pdet_data = get_pdet_municipalities()
    pa_mappings = pdet_data.get("policy_area_mappings", {})
    
    pa_key = f"{policy_area_id}" if policy_area_id.startswith("PA") else f"PA{policy_area_id}"
    pa_data = pa_mappings.get(pa_key, {})
    relevant_subregion_ids = set(pa_data.get("relevant_subregions", []))
    
    municipalities = []
    for subregion in pdet_data.get("subregions", []):
        if subregion["subregion_id"] in relevant_subregion_ids:
            municipalities.extend(subregion.get("municipalities", []))
    
    return municipalities


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
    # Municipal governance data structures
    "MunicipalCategory",
    "PdetPillar",
    "PdetInfo",
    "SgpComponent",
    "MunicipalGovernance",
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
    # Municipal governance API functions
    "get_municipal_governance",
    "get_pdet_info",
    "get_municipal_category",
    "get_sgp_components",
    "get_ocad_paz_approvals",
    "get_pdet_pillar",
    # PDET municipalities API functions
    "get_pdet_municipalities",
    "get_pdet_subregions",
    "get_pdet_municipalities_for_policy_area",
]
