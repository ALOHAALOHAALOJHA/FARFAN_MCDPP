"""
Cross-Cutting Themes Module
============================

This module provides cross-cutting themes that apply across all
dimensions and policy areas in the FARFAN questionnaire.

Cross-cutting themes are horizontal considerations that must be
taken into account across all policy analysis, regardless of the
specific dimension or policy area being evaluated.

Available Themes:
------------------
- CC_ENFOQUE_DIFERENCIAL: Differential approach for specific groups
- CC_PERSPECTIVA_GENERO: Gender perspective and equality
- CC_ENTORNO_TERRITORIAL: Territorial and environmental context
- CC_PARTICIPACION_CIUDADANA: Citizen participation mechanisms
- CC_COHERENCIA_NORMATIVA: Legal and regulatory alignment
- CC_SOSTENIBILIDAD_PRESUPUESTAL: Budgetary sustainability
- CC_INTEROPERABILIDAD: Institutional interoperability
- CC_MECANISMOS_SEGUIMIENTO: Monitoring and evaluation mechanisms

Usage:
------
    from canonic_questionnaire_central.cross_cutting import (
        get_cross_cutting_themes,
        get_themes_for_policy_area,
        validate_themes_coverage,
    )

    # Get all themes
    themes = get_cross_cutting_themes()

    # Get themes for a specific policy area
    pa01_themes = get_themes_for_policy_area("PA01")

    # Validate coverage of themes
    is_valid, missing = validate_themes_coverage("PA01", covered_themes)

Author: F.A.R.F.A.N Pipeline Team
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Type aliases for better readability
ThemeId = str
PolicyAreaId = str
DimensionId = str

# Path to cross-cutting themes configuration
_CROSS_CUTTING_DIR = Path(__file__).parent
_THEMES_FILE = _CROSS_CUTTING_DIR / "cross_cutting_themes.json"


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CrossCuttingTheme:
    """A cross-cutting theme that applies across dimensions and policy areas."""
    theme_id: str
    name: str
    description: str
    i18n: dict[str, Any]
    applies_to: dict[str, list[str]]
    indicators: list[str]
    validation_rules: dict[str, Any]

    def applies_to_dimension(self, dimension_id: str) -> bool:
        """Check if theme applies to a dimension."""
        return dimension_id in self.applies_to.get("dimensions", [])

    def applies_to_policy_area(self, policy_area_id: str) -> bool:
        """Check if theme applies to a policy area."""
        return policy_area_id in self.applies_to.get("policy_areas", [])

    def is_required_for(self, policy_area_id: str) -> bool:
        """Check if theme is required for a policy area."""
        rules = self.validation_rules
        return (
            policy_area_id in rules.get("required_for", []) or
            rules.get("required_for_all", False)
        )

    def is_recommended_for(self, policy_area_id: str) -> bool:
        """Check if theme is recommended for a policy area."""
        rules = self.validation_rules
        return policy_area_id in rules.get("recommended_for", [])


@dataclass
class ThemeCombination:
    """A combination of cross-cutting themes."""
    combination_id: str
    themes: list[str]
    description: str
    priority: str


# =============================================================================
# CONFIGURATION LOADER
# =============================================================================

@dataclass
class CrossCuttingConfig:
    """Configuration for cross-cutting themes."""
    themes: list[CrossCuttingTheme]
    theme_combinations: list[ThemeCombination]
    validation_rules: dict[str, Any]

    @classmethod
    def from_json(cls, json_path: Path | None = None) -> "CrossCuttingConfig":
        """Load configuration from JSON file."""
        if json_path is None:
            json_path = _THEMES_FILE

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        themes = [
            CrossCuttingTheme(**theme_data)
            for theme_data in data.get("themes", [])
        ]

        combinations = [
            ThemeCombination(**combo_data)
            for combo_data in data.get("theme_combinations", [])
        ]

        validation_rules = data.get("validation_rules", {})

        return cls(
            themes=themes,
            theme_combinations=combinations,
            validation_rules=validation_rules
        )

    def get_theme_by_id(self, theme_id: str) -> CrossCuttingTheme | None:
        """Get theme by ID."""
        for theme in self.themes:
            if theme.theme_id == theme_id:
                return theme
        return None

    def get_themes_for_policy_area(
        self,
        policy_area_id: PolicyAreaId
    ) -> list[CrossCuttingTheme]:
        """Get all themes that apply to a policy area."""
        return [
            theme for theme in self.themes
            if theme.applies_to_policy_area(policy_area_id)
        ]

    def get_required_themes_for_policy_area(
        self,
        policy_area_id: PolicyAreaId
    ) -> list[CrossCuttingTheme]:
        """Get required themes for a policy area."""
        return [
            theme for theme in self.themes
            if theme.is_required_for(policy_area_id)
        ]

    def get_recommended_themes_for_policy_area(
        self,
        policy_area_id: PolicyAreaId
    ) -> list[CrossCuttingTheme]:
        """Get recommended themes for a policy area."""
        return [
            theme for theme in self.themes
            if theme.is_recommended_for(policy_area_id)
        ]


# =============================================================================
# GLOBAL CONFIGURATION INSTANCE
# =============================================================================

_config: CrossCuttingConfig | None = None


def _get_config() -> CrossCuttingConfig:
    """Get or load global configuration."""
    global _config
    if _config is None:
        _config = CrossCuttingConfig.from_json()
    return _config


# =============================================================================
# PUBLIC API
# =============================================================================

def get_cross_cutting_themes() -> list[CrossCuttingTheme]:
    """Get all cross-cutting themes.

    Returns:
        List of all cross-cutting themes
    """
    config = _get_config()
    return config.themes


def get_theme_by_id(theme_id: ThemeId) -> CrossCuttingTheme | None:
    """Get a specific theme by ID.

    Args:
        theme_id: Theme identifier (e.g., "CC_PERSPECTIVA_GENERO")

    Returns:
        CrossCuttingTheme or None if not found
    """
    config = _get_config()
    return config.get_theme_by_id(theme_id)


def get_themes_for_policy_area(
    policy_area_id: PolicyAreaId
) -> list[CrossCuttingTheme]:
    """Get all themes that apply to a policy area.

    Args:
        policy_area_id: Policy area identifier (e.g., "PA01")

    Returns:
        List of themes that apply to the policy area
    """
    config = _get_config()
    return config.get_themes_for_policy_area(policy_area_id)


def get_required_themes_for_policy_area(
    policy_area_id: PolicyAreaId
) -> list[CrossCuttingTheme]:
    """Get required themes for a policy area.

    Args:
        policy_area_id: Policy area identifier

    Returns:
        List of required themes
    """
    config = _get_config()
    return config.get_required_themes_for_policy_area(policy_area_id)


def get_recommended_themes_for_policy_area(
    policy_area_id: PolicyAreaId
) -> list[CrossCuttingTheme]:
    """Get recommended themes for a policy area.

    Args:
        policy_area_id: Policy area identifier

    Returns:
        List of recommended themes
    """
    config = _get_config()
    return config.get_recommended_themes_for_policy_area(policy_area_id)


def get_theme_combinations() -> list[ThemeCombination]:
    """Get all theme combinations.

    Returns:
        List of theme combinations
    """
    config = _get_config()
    return config.theme_combinations


def validate_themes_coverage(
    policy_area_id: PolicyAreaId,
    covered_themes: list[str]
) -> tuple[bool, list[str], list[str]]:
    """Validate coverage of required themes.

    Args:
        policy_area_id: Policy area identifier
        covered_themes: List of theme IDs that are covered

    Returns:
        Tuple of (is_valid, missing_required, missing_recommended)
    """
    required = get_required_themes_for_policy_area(policy_area_id)
    recommended = get_recommended_themes_for_policy_area(policy_area_id)

    required_ids = [t.theme_id for t in required]
    recommended_ids = [t.theme_id for t in recommended]

    missing_required = [
        t_id for t_id in required_ids
        if t_id not in covered_themes
    ]

    missing_recommended = [
        t_id for t_id in recommended_ids
        if t_id not in covered_themes
    ]

    is_valid = len(missing_required) == 0

    return is_valid, missing_required, missing_recommended


def get_minimum_themes_count() -> int:
    """Get minimum number of themes per policy area."""
    config = _get_config()
    return config.validation_rules.get("minimum_themes_per_policy_area", 3)


def get_required_themes_all() -> list[str]:
    """Get themes required for all policy areas."""
    config = _get_config()
    return config.validation_rules.get("required_themes_all", [])


def get_theme_priority_order() -> list[str]:
    """Get priority order for themes."""
    config = _get_config()
    return config.validation_rules.get("theme_priority_order", [])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data structures
    "CrossCuttingTheme",
    "ThemeCombination",
    "CrossCuttingConfig",
    # API functions
    "get_cross_cutting_themes",
    "get_theme_by_id",
    "get_themes_for_policy_area",
    "get_required_themes_for_policy_area",
    "get_recommended_themes_for_policy_area",
    "get_theme_combinations",
    "validate_themes_coverage",
    "get_minimum_themes_count",
    "get_required_themes_all",
    "get_theme_priority_order",
    # Type aliases
    "ThemeId",
    "PolicyAreaId",
    "DimensionId",
]
