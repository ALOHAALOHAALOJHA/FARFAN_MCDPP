"""
Unit Layer Configuration Loader.

Loads UnitLayerConfig from JSON file.
"""

import json
from pathlib import Path
from typing import Any

from farfan_pipeline.core.calibration.unit_layer import UnitLayerConfig


def load_unit_layer_config(config_path: str | Path | None = None) -> UnitLayerConfig:
    """
    Load Unit Layer configuration from JSON file.

    Args:
        config_path: Path to unit_layer_config.json. If None, uses default location.

    Returns:
        UnitLayerConfig instance

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config validation fails
    """
    if config_path is None:
        config_path = Path("system/config/calibration/unit_layer_config.json")
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Unit layer config not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = json.load(f)

    # Extract configuration sections
    weights = data.get("component_weights", {})
    aggregation = data.get("aggregation", {})
    gates = data.get("hard_gates", {})
    gaming = data.get("anti_gaming_thresholds", {})
    s_config = data.get("S_structural_compliance", {})
    m_config = data.get("M_mandatory_sections", {})
    i_config = data.get("I_indicator_quality", {})
    p_config = data.get("P_ppi_completeness", {})

    # Build UnitLayerConfig
    config_dict: dict[str, Any] = {
        # Component weights
        "w_S": weights.get("w_S", 0.25),
        "w_M": weights.get("w_M", 0.25),
        "w_I": weights.get("w_I", 0.25),
        "w_P": weights.get("w_P", 0.25),
        # Aggregation
        "aggregation_type": aggregation.get("aggregation_type", "geometric_mean"),
        # Hard gates
        "require_ppi_presence": gates.get("require_ppi_presence", True),
        "require_indicator_matrix": gates.get("require_indicator_matrix", True),
        "min_structural_compliance": gates.get("min_structural_compliance", 0.5),
        "i_struct_hard_gate": gates.get("i_struct_hard_gate", 0.7),
        "p_struct_hard_gate": gates.get("p_struct_hard_gate", 0.7),
        # Anti-gaming
        "max_placeholder_ratio": gaming.get("max_placeholder_ratio", 0.10),
        "min_unique_values_ratio": gaming.get("min_unique_values_ratio", 0.5),
        "min_number_density": gaming.get("min_number_density", 0.02),
        "gaming_penalty_cap": gaming.get("gaming_penalty_cap", 0.3),
        # S parameters
        "w_block_coverage": s_config.get("w_block_coverage", 0.5),
        "w_hierarchy": s_config.get("w_hierarchy", 0.25),
        "w_order": s_config.get("w_order", 0.25),
        "min_block_tokens": s_config.get("min_block_tokens", 100),
        "min_block_numbers": s_config.get("min_block_numbers", 3),
        "hierarchy_excellent_threshold": s_config.get(
            "hierarchy_excellent_threshold", 0.9
        ),
        "hierarchy_acceptable_threshold": s_config.get(
            "hierarchy_acceptable_threshold", 0.6
        ),
        # M parameters
        "critical_sections_weight": m_config.get("critical_sections_weight", 2.0),
    }

    # Extract section-specific M parameters
    sections = m_config.get("sections", {})
    if "Diagnóstico" in sections:
        diag = sections["Diagnóstico"]
        config_dict["diagnostico_min_tokens"] = diag.get("min_tokens", 800)
        config_dict["diagnostico_min_keywords"] = diag.get("min_keywords", 3)
        config_dict["diagnostico_min_numbers"] = diag.get("min_numbers", 10)
        config_dict["diagnostico_min_sources"] = diag.get("min_sources", 2)

    if "Parte Estratégica" in sections:
        estrat = sections["Parte Estratégica"]
        config_dict["estrategica_min_tokens"] = estrat.get("min_tokens", 600)
        config_dict["estrategica_min_keywords"] = estrat.get("min_keywords", 2)
        config_dict["estrategica_min_numbers"] = estrat.get("min_numbers", 5)

    if "PPI" in sections:
        ppi_sect = sections["PPI"]
        config_dict["ppi_section_min_tokens"] = ppi_sect.get("min_tokens", 400)
        config_dict["ppi_section_min_keywords"] = ppi_sect.get("min_keywords", 2)
        config_dict["ppi_section_min_numbers"] = ppi_sect.get("min_numbers", 8)

    if "Seguimiento" in sections:
        seg = sections["Seguimiento"]
        config_dict["seguimiento_min_tokens"] = seg.get("min_tokens", 300)
        config_dict["seguimiento_min_keywords"] = seg.get("min_keywords", 2)
        config_dict["seguimiento_min_numbers"] = seg.get("min_numbers", 3)

    if "Marco Normativo" in sections:
        marco = sections["Marco Normativo"]
        config_dict["marco_normativo_min_tokens"] = marco.get("min_tokens", 200)
        config_dict["marco_normativo_min_keywords"] = marco.get("min_keywords", 1)

    # I parameters
    config_dict["w_i_struct"] = i_config.get("w_i_struct", 0.4)
    config_dict["w_i_link"] = i_config.get("w_i_link", 0.3)
    config_dict["w_i_logic"] = i_config.get("w_i_logic", 0.3)

    i_struct = i_config.get("i_struct", {})
    config_dict["i_critical_fields_weight"] = i_struct.get(
        "critical_fields_weight", 2.0
    )
    config_dict["i_placeholder_penalty_multiplier"] = i_struct.get(
        "placeholder_penalty_multiplier", 3.0
    )

    i_link = i_config.get("i_link", {})
    config_dict["i_fuzzy_match_threshold"] = i_link.get("fuzzy_match_threshold", 0.85)

    i_logic = i_config.get("i_logic", {})
    config_dict["i_valid_lb_year_min"] = i_logic.get("valid_lb_year_min", 2015)
    config_dict["i_valid_lb_year_max"] = i_logic.get("valid_lb_year_max", 2024)

    # P parameters
    config_dict["w_p_presence"] = p_config.get("w_p_presence", 0.2)
    config_dict["w_p_structure"] = p_config.get("w_p_structure", 0.4)
    config_dict["w_p_consistency"] = p_config.get("w_p_consistency", 0.4)

    p_struct = p_config.get("p_struct", {})
    config_dict["p_nonzero_row_threshold"] = p_struct.get("nonzero_row_threshold", 0.80)

    p_cons = p_config.get("p_consistency", {})
    config_dict["p_accounting_tolerance"] = p_cons.get("accounting_tolerance", 0.01)
    config_dict["p_trazabilidad_threshold"] = p_cons.get("trazabilidad_threshold", 0.80)

    return UnitLayerConfig(**config_dict)


def save_unit_layer_config(config: UnitLayerConfig, output_path: str | Path) -> None:
    """
    Save UnitLayerConfig to JSON file.

    Args:
        config: UnitLayerConfig instance
        output_path: Path to save JSON file
    """
    output_path = Path(output_path)

    data = {
        "_metadata": {
            "version": "1.0.0",
            "description": "Unit Layer (@u) Configuration - S/M/I/P Components",
            "notes": "Auto-generated from UnitLayerConfig",
        },
        "component_weights": {
            "w_S": config.w_S,
            "w_M": config.w_M,
            "w_I": config.w_I,
            "w_P": config.w_P,
        },
        "aggregation": {"aggregation_type": config.aggregation_type},
        "hard_gates": {
            "require_ppi_presence": config.require_ppi_presence,
            "require_indicator_matrix": config.require_indicator_matrix,
            "min_structural_compliance": config.min_structural_compliance,
            "i_struct_hard_gate": config.i_struct_hard_gate,
            "p_struct_hard_gate": config.p_struct_hard_gate,
        },
        "anti_gaming_thresholds": {
            "max_placeholder_ratio": config.max_placeholder_ratio,
            "min_unique_values_ratio": config.min_unique_values_ratio,
            "min_number_density": config.min_number_density,
            "gaming_penalty_cap": config.gaming_penalty_cap,
        },
        "S_structural_compliance": {
            "w_block_coverage": config.w_block_coverage,
            "w_hierarchy": config.w_hierarchy,
            "w_order": config.w_order,
            "min_block_tokens": config.min_block_tokens,
            "min_block_numbers": config.min_block_numbers,
            "hierarchy_excellent_threshold": config.hierarchy_excellent_threshold,
            "hierarchy_acceptable_threshold": config.hierarchy_acceptable_threshold,
        },
        "M_mandatory_sections": {
            "critical_sections_weight": config.critical_sections_weight,
            "sections": {
                "Diagnóstico": {
                    "min_tokens": config.diagnostico_min_tokens,
                    "min_keywords": config.diagnostico_min_keywords,
                    "min_numbers": config.diagnostico_min_numbers,
                    "min_sources": config.diagnostico_min_sources,
                },
                "Parte Estratégica": {
                    "min_tokens": config.estrategica_min_tokens,
                    "min_keywords": config.estrategica_min_keywords,
                    "min_numbers": config.estrategica_min_numbers,
                },
                "PPI": {
                    "min_tokens": config.ppi_section_min_tokens,
                    "min_keywords": config.ppi_section_min_keywords,
                    "min_numbers": config.ppi_section_min_numbers,
                },
                "Seguimiento": {
                    "min_tokens": config.seguimiento_min_tokens,
                    "min_keywords": config.seguimiento_min_keywords,
                    "min_numbers": config.seguimiento_min_numbers,
                },
                "Marco Normativo": {
                    "min_tokens": config.marco_normativo_min_tokens,
                    "min_keywords": config.marco_normativo_min_keywords,
                },
            },
        },
        "I_indicator_quality": {
            "w_i_struct": config.w_i_struct,
            "w_i_link": config.w_i_link,
            "w_i_logic": config.w_i_logic,
            "i_struct": {
                "critical_fields_weight": config.i_critical_fields_weight,
                "placeholder_penalty_multiplier": config.i_placeholder_penalty_multiplier,
            },
            "i_link": {"fuzzy_match_threshold": config.i_fuzzy_match_threshold},
            "i_logic": {
                "valid_lb_year_min": config.i_valid_lb_year_min,
                "valid_lb_year_max": config.i_valid_lb_year_max,
            },
        },
        "P_ppi_completeness": {
            "w_p_presence": config.w_p_presence,
            "w_p_structure": config.w_p_structure,
            "w_p_consistency": config.w_p_consistency,
            "p_struct": {"nonzero_row_threshold": config.p_nonzero_row_threshold},
            "p_consistency": {
                "accounting_tolerance": config.p_accounting_tolerance,
                "trazabilidad_threshold": config.p_trazabilidad_threshold,
            },
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
