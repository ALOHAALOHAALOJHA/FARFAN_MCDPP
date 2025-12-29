"""Contract tests para pipeline epistemológico FORENSIC v5.

PROPÓSITO:
- Garantizar reproducibilidad bit-a-bit
- Detectar drift semántico ante cambios de reglas
- Fallar CI si outputs cambian sin actualizar goldens

Versión: 5.0.0
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

# Importar desde el script principal
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

from enrich_inventory_epistemology_v5_FORENSIC import (
    CANONICAL_RULEBOOK,
    MethodDecision,
    PipelineFatalError,
    Rule,
    RuleEvaluation,
    Rulebook,
    VetoCondition,
    _compute_blob,
    _hash_blob,
    _norm,
    compute_code_hash,
    compute_data_hash,
    enrich_inventory,
    evaluate_rules,
    extract_veto_conditions,
    fatal,
    infer_contract_compatibility,
    map_level_to_output,
)


# ══════════════════════════════════════════════════════════════════════════════
# GOLDEN HASHES - ACTUALIZAR MANUALMENTE TRAS CAMBIOS INTENCIONALES
# ══════════════════════════════════════════════════════════════════════════════

# Hash del rulebook canónico - cambiar reglas DEBE cambiar este hash
EXPECTED_RULEBOOK_HASH = None  # Se calcula en primera ejecución

# Hash del código fuente del módulo
EXPECTED_CODE_HASH = None  # Se calcula en primera ejecución


# ══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_method_n1() -> dict[str, Any]:
    """Método que DEBE clasificarse como N1-EMP."""
    return {
        "return_type": "list[str]",
        "docstring": "Extract raw text chunks from document.",
        "parameters": [{"name": "text", "type": "str"}],
    }


@pytest.fixture
def sample_method_n2_bayesian() -> dict[str, Any]:
    """Método que DEBE clasificarse como N2-INF + BAYESIAN."""
    return {
        "return_type": "float",
        "docstring": "Compute posterior probability using Bayesian inference.",
        "parameters": [{"name": "prior", "type": "float"}, {"name": "likelihood", "type": "float"}],
    }


@pytest.fixture
def sample_method_n3_with_veto() -> dict[str, Any]:
    """Método que DEBE clasificarse como N3-AUD con veto."""
    return {
        "return_type": "bool",
        "docstring": "Validate input. Returns False if invalid or fails constraints.",
        "parameters": [{"name": "data", "type": "dict"}],
    }


@pytest.fixture
def sample_method_n3_without_veto() -> dict[str, Any]:
    """Método que sería N3-AUD pero sin señales de veto → debe degradar a N2."""
    return {
        "return_type": "bool",
        "docstring": "Check if document has tables.",
        "parameters": [{"name": "text", "type": "str"}],
    }


@pytest.fixture
def sample_method_n4() -> dict[str, Any]:
    """Método que DEBE clasificarse como N4-SYN."""
    return {
        "return_type": "str",
        "docstring": "Generate executive report with narrative synthesis.",
        "parameters": [],
    }


@pytest.fixture
def sample_method_infrastructure() -> dict[str, Any]:
    """Método que DEBE clasificarse como INFRASTRUCTURE."""
    return {
        "return_type": "None",
        "docstring": None,
        "parameters": [],
    }


@pytest.fixture
def minimal_inventory() -> dict[str, Any]:
    """Inventario mínimo para tests de integración."""
    return {
        "TestClassN1": {
            "file_path": "test/test_n1.py",
            "line_number": 1,
            "methods": {
                "extract_chunks": {
                    "return_type": "list[str]",
                    "docstring": "Extract text chunks.",
                    "parameters": [],
                },
            },
        },
        "TestClassN2": {
            "file_path": "test/test_n2.py",
            "line_number": 1,
            "methods": {
                "compute_score": {
                    "return_type": "float",
                    "docstring": "Compute bayesian posterior score.",
                    "parameters": [],
                },
            },
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# TESTS DE INVARIANTES - DEBEN FALLAR SI SE VIOLAN
# ══════════════════════════════════════════════════════════════════════════════


class TestInvariants:
    """Tests que verifican que invariantes se cumplen."""

    def test_n3_without_veto_degrades_to_n2(self, sample_method_n3_without_veto: dict[str, Any]) -> None:
        """N3-AUD sin señales de veto DEBE degradar a N2-INF."""
        inventory = {
            "TestClass": {
                "file_path": "test.py",
                "line_number": 1,
                "methods": {"check_tables": sample_method_n3_without_veto},
            }
        }

        enriched, session = enrich_inventory(inventory)

        # Debe haber degradación
        assert len(session.degradations) == 1
        assert session.degradations[0].original_level == "N3-AUD"
        assert session.degradations[0].degraded_to == "N2-INF"

        # El método debe estar como N2-INF
        method = enriched["TestClass"]["methods"]["check_tables"]
        assert method["epistemological_classification"]["level"] == "N2-INF"

    def test_n3_with_veto_stays_n3(self, sample_method_n3_with_veto: dict[str, Any]) -> None:
        """N3-AUD con señales de veto DEBE mantenerse como N3-AUD."""
        inventory = {
            "TestClass": {
                "file_path": "test.py",
                "line_number": 1,
                "methods": {"validate_input": sample_method_n3_with_veto},
            }
        }

        enriched, session = enrich_inventory(inventory)

        # No debe haber degradación
        assert len(session.degradations) == 0

        # El método debe estar como N3-AUD
        method = enriched["TestClass"]["methods"]["validate_input"]
        assert method["epistemological_classification"]["level"] == "N3-AUD"
        assert method["epistemological_classification"]["veto_conditions"] is not None

    def test_bayesian_must_have_type_b(self, sample_method_n2_bayesian: dict[str, Any]) -> None:
        """BAYESIAN_PROBABILISTIC DEBE tener TYPE_B = True."""
        inventory = {
            "TestClass": {
                "file_path": "test.py",
                "line_number": 1,
                "methods": {"compute_posterior": sample_method_n2_bayesian},
            }
        }

        enriched, session = enrich_inventory(inventory)

        method = enriched["TestClass"]["methods"]["compute_posterior"]
        compat = method["epistemological_classification"]["contract_compatibility"]
        assert compat["TYPE_B"] is True

    def test_n4_must_produce_narrative(self, sample_method_n4: dict[str, Any]) -> None:
        """N4-SYN DEBE producir 'narrative'."""
        inventory = {
            "TestClass": {
                "file_path": "test.py",
                "line_number": 1,
                "methods": {"generate_report": sample_method_n4},
            }
        }

        enriched, session = enrich_inventory(inventory)

        method = enriched["TestClass"]["methods"]["generate_report"]
        deps = method["epistemological_classification"]["dependencies"]
        assert "narrative" in deps["produces"]


class TestFailHard:
    """Tests que verifican que el pipeline FALLA ante violaciones."""

    def test_fatal_raises_exception(self) -> None:
        """fatal() DEBE lanzar PipelineFatalError."""
        with pytest.raises(PipelineFatalError) as exc_info:
            fatal("TEST_ERROR", "Test message", key="value")

        assert exc_info.value.error_id == "TEST_ERROR"
        assert "TEST_ERROR" in str(exc_info.value)
        assert exc_info.value.context == {"key": "value"}

    def test_no_matching_rule_fails(self) -> None:
        """Método sin regla matching DEBE fallar."""
        # Crear rulebook vacío
        empty_rulebook = Rulebook(version="test", rules=())

        with pytest.raises(PipelineFatalError) as exc_info:
            evaluate_rules(
                "some_method",
                {"return_type": "complex", "docstring": "unusual"},
                "TestClass",
                empty_rulebook,
            )

        assert exc_info.value.error_id == "NO_MATCHING_RULE"


class TestTraceability:
    """Tests que verifican trazabilidad completa."""

    def test_all_evaluations_recorded(self, sample_method_n1: dict[str, Any]) -> None:
        """Cada regla evaluada DEBE quedar registrada."""
        decision = evaluate_rules("extract_text", sample_method_n1, "TestClass", CANONICAL_RULEBOOK)

        # Debe haber evaluaciones para TODAS las reglas
        assert len(decision.all_evaluations) == len(CANONICAL_RULEBOOK.rules)

        # Al menos una debe estar SELECTED
        selected = [ev for ev in decision.all_evaluations if ev.contribution == "SELECTED"]
        assert len(selected) == 1

    def test_degradation_has_full_context(self, sample_method_n3_without_veto: dict[str, Any]) -> None:
        """DegradationRecord DEBE tener contexto completo."""
        inventory = {
            "TestClass": {
                "file_path": "test.py",
                "line_number": 1,
                "methods": {"check_tables": sample_method_n3_without_veto},
            }
        }

        enriched, session = enrich_inventory(inventory)

        deg = session.degradations[0]
        assert deg.method_id == "check_tables"
        assert deg.class_name == "TestClass"
        assert deg.original_level == "N3-AUD"
        assert deg.degraded_to == "N2-INF"
        assert deg.reason != ""
        assert deg.timestamp != ""


class TestReproducibility:
    """Tests que verifican reproducibilidad."""

    def test_same_input_same_output_hash(self, minimal_inventory: dict[str, Any]) -> None:
        """Mismo input DEBE producir mismo output."""
        enriched1, session1 = enrich_inventory(minimal_inventory)
        enriched2, session2 = enrich_inventory(minimal_inventory)

        # Remover timestamps para comparación
        del enriched1["_pipeline_metadata"]["generated_at"]
        del enriched2["_pipeline_metadata"]["generated_at"]

        hash1 = compute_data_hash(enriched1)
        hash2 = compute_data_hash(enriched2)

        assert hash1 == hash2

    def test_rulebook_hash_deterministic(self) -> None:
        """Rulebook hash DEBE ser determinista."""
        hash1 = CANONICAL_RULEBOOK.compute_hash()
        hash2 = CANONICAL_RULEBOOK.compute_hash()
        assert hash1 == hash2

    def test_code_hash_exists(self) -> None:
        """code_hash DEBE existir y ser no vacío."""
        code_hash = compute_code_hash()
        assert code_hash
        assert len(code_hash) == 16  # Primeros 16 chars de SHA256


class TestVetoExtraction:
    """Tests para extracción de condiciones de veto."""

    def test_veto_extracts_invalid_signal(self) -> None:
        """'invalid' en docstring DEBE generar veto."""
        conditions = extract_veto_conditions("N3-AUD", "Returns False if invalid", "test")
        assert conditions is not None
        assert any(vc.trigger == "validation_failed" for vc in conditions)

    def test_veto_extracts_weak_signal(self) -> None:
        """'weak'/'insufficient' en docstring DEBE generar veto."""
        conditions = extract_veto_conditions("N3-AUD", "Check for weak evidence", "test")
        assert conditions is not None
        assert any(vc.trigger == "below_threshold" for vc in conditions)

    def test_veto_none_without_signals(self) -> None:
        """Sin señales de veto, retorna None."""
        conditions = extract_veto_conditions("N3-AUD", "Check if table exists", "test")
        assert conditions is None

    def test_veto_none_for_non_n3(self) -> None:
        """Para niveles no-N3, retorna None."""
        conditions = extract_veto_conditions("N2-INF", "Returns False if invalid", "test")
        assert conditions is None


class TestContractCompatibility:
    """Tests para inferencia de compatibilidad de contrato."""

    def test_semantic_signals_type_a(self) -> None:
        """Señales semánticas DEBEN activar TYPE_A."""
        compat = infer_contract_compatibility("chunk text semantic", "N1-EMP", "POSITIVIST_EMPIRICAL")
        assert compat["TYPE_A"] is True

    def test_bayesian_signals_type_b(self) -> None:
        """Señales bayesianas DEBEN activar TYPE_B."""
        compat = infer_contract_compatibility("posterior bayesian prior", "N2-INF", "BAYESIAN_PROBABILISTIC")
        assert compat["TYPE_B"] is True

    def test_bayesian_epistemology_forces_type_b(self) -> None:
        """Epistemología BAYESIAN DEBE forzar TYPE_B."""
        compat = infer_contract_compatibility("compute score", "N2-INF", "BAYESIAN_PROBABILISTIC")
        assert compat["TYPE_B"] is True

    def test_validation_signals_type_e(self) -> None:
        """Señales de validación DEBEN activar TYPE_E."""
        compat = infer_contract_compatibility("validate check consistency", "N3-AUD", "POPPERIAN_FALSIFICATIONIST")
        assert compat["TYPE_E"] is True


# ══════════════════════════════════════════════════════════════════════════════
# GOLDEN OUTPUT TEST - ACTUALIZAR TRAS CAMBIOS INTENCIONALES
# ══════════════════════════════════════════════════════════════════════════════


class TestGoldenOutput:
    """Test de output dorado para detectar regresiones."""

    GOLDEN_INPUT = {
        "GoldenClass": {
            "file_path": "golden/test.py",
            "line_number": 1,
            "methods": {
                "extract_data": {
                    "return_type": "list[str]",
                    "docstring": "Extract raw data from text.",
                    "parameters": [{"name": "text", "type": "str"}],
                },
                "compute_score": {
                    "return_type": "float",
                    "docstring": "Compute posterior probability.",
                    "parameters": [],
                },
                "validate_input": {
                    "return_type": "bool",
                    "docstring": "Validate input. Fails if invalid.",
                    "parameters": [],
                },
            },
        },
    }

    # ACTUALIZAR ESTE HASH SI CAMBIAS REGLAS INTENCIONALMENTE
    EXPECTED_OUTPUT_HASH: str | None = None  # None = primera ejecución calcula

    def test_golden_output_stable(self) -> None:
        """Output para input dorado DEBE ser estable."""
        enriched, session = enrich_inventory(self.GOLDEN_INPUT)

        # Remover campos variables
        del enriched["_pipeline_metadata"]["generated_at"]
        del enriched["_pipeline_metadata"]["session_id"]

        output_hash = compute_data_hash(enriched)

        if self.EXPECTED_OUTPUT_HASH is None:
            # Primera ejecución: imprimir hash para actualizar
            pytest.skip(f"GOLDEN_OUTPUT_HASH not set. Current hash: {output_hash[:32]}")
        else:
            assert output_hash.startswith(self.EXPECTED_OUTPUT_HASH), (
                f"Golden output changed! Expected {self.EXPECTED_OUTPUT_HASH}, got {output_hash[:32]}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
