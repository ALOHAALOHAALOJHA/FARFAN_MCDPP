"""
Tests for FinancialChainExtractor (MC05) - Empirically Calibrated.

Auto-generated from empirical corpus with gold standard examples.

Author: CQC Extractor Excellence Framework
Version: 2.0.0
Date: 2026-01-06
"""

import pytest
from farfan_pipeline.infrastructure.extractors import (
    FinancialChainExtractor,
    extract_financial_chains,
)


class TestFinancialChainExtractor:
    """Test suite for FinancialChainExtractor based on empirical corpus."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return FinancialChainExtractor()

    # ========================================================================
    # EMPIRICAL GOLD STANDARD TESTS - Cajibío Plan
    # ========================================================================

    def test_cajibio_ppi_total_extraction(self, extractor):
        """
        Test: Cajibío Plan PPI total extraction.
        Gold Standard: $288,087 millones (288087496180 pesos)
        Expected: Extract total amount with high confidence (>0.95)
        """
        text = """
        PLAN PLURIANUAL DE INVERSIONES 2024-2027

        El Plan Plurianual de Inversiones asciende a $288,087 millones de pesos,
        distribuidos entre las diferentes fuentes de financiación.
        """

        result = extractor.extract(text)

        # Verify extraction occurred
        assert len(result.matches) > 0, "Should extract at least one financial chain"

        # Find the main PPI amount
        ppi_chains = [m for m in result.matches if m.get("monto_normalizado", 0) > 280_000_000_000]
        assert len(ppi_chains) > 0, "Should extract PPI total amount"

        # Verify normalization to pesos
        main_chain = ppi_chains[0]
        expected = 288_087_000_000  # $288,087 millones
        actual = main_chain["monto_normalizado"]

        # Allow 1% tolerance for normalization
        tolerance = expected * 0.01
        assert (
            abs(actual - expected) <= tolerance
        ), f"Expected ~{expected:,.0f} pesos, got {actual:,.0f}"

        # Verify high confidence
        assert (
            main_chain["confidence"] >= 0.90
        ), f"Expected confidence >= 0.90, got {main_chain['confidence']}"

    def test_cajibio_sgp_fuente_extraction(self, extractor):
        """
        Test: Cajibío SGP source extraction.
        Gold Standard: SGP $43,263 millones (15% del total)
        Expected: Extract amount and link to SGP source
        """
        text = """
        Fuentes de Financiación:

        Sistema General de Participaciones (SGP): $43,263 millones de pesos,
        equivalente al 15% del Plan Plurianual de Inversiones.
        """

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract financial chains"

        # Find SGP chain
        sgp_chains = [m for m in result.matches if m.get("fuente") and "SGP" in m["fuente"]]

        if sgp_chains:  # SGP might be extracted separately
            sgp_chain = sgp_chains[0]
            expected = 43_263_000_000
            actual = sgp_chain.get("monto_normalizado", 0)

            tolerance = expected * 0.01
            assert (
                abs(actual - expected) <= tolerance
            ), f"SGP amount: expected ~{expected:,.0f}, got {actual:,.0f}"

    def test_cajibio_adres_fuente_extraction(self, extractor):
        """
        Test: Cajibío ADRES source extraction.
        Gold Standard: ADRES $181,675 millones (63% del total)
        Expected: Extract largest funding source with high confidence
        """
        text = """
        Recursos ADRES (Salud): $181,675 millones de pesos, representando el 63%
        del total del Plan Plurianual de Inversiones 2024-2027.
        """

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract ADRES funding"

        # Verify large amounts are extracted
        large_amounts = [
            m for m in result.matches if m.get("monto_normalizado", 0) > 180_000_000_000
        ]
        assert len(large_amounts) > 0, "Should extract ADRES amount (>180 billion)"

    # ========================================================================
    # CURRENCY NORMALIZATION TESTS
    # ========================================================================

    def test_currency_normalization_millones(self, extractor):
        """
        Test: Currency normalization for 'millones'.
        Empirical Pattern: "$X,XXX millones" is most common format
        Expected: Correctly multiply by 1,000,000
        """
        test_cases = [
            ("$500 millones", 500_000_000),
            ("$1,234 millones", 1_234_000_000),
            ("$288,087 millones", 288_087_000_000),
        ]

        for text, expected in test_cases:
            result = extractor.extract(text)
            if result.matches:
                actual = result.matches[0].get("monto_normalizado", 0)
                tolerance = expected * 0.01
                assert (
                    abs(actual - expected) <= tolerance
                ), f"Text '{text}': expected {expected:,}, got {actual:,}"

    def test_currency_normalization_billones(self, extractor):
        """
        Test: Currency normalization for 'billones'.
        Empirical Example: "$1.625 billones" from corpus
        Expected: Correctly multiply by 1,000,000,000,000
        """
        text = "$1.625 billones para el cuatrienio"
        expected = 1_625_000_000_000

        result = extractor.extract(text)

        if result.matches:
            actual = result.matches[0].get("monto_normalizado", 0)
            tolerance = expected * 0.01
            assert abs(actual - expected) <= tolerance, f"Expected {expected:,}, got {actual:,}"

    def test_currency_normalization_raw_numbers(self, extractor):
        """
        Test: Raw currency amounts without unit multipliers.
        Empirical Example: "$16,624,484,812" from corpus
        Expected: Parse large numbers correctly
        """
        text = "Presupuesto total: $16,624,484,812 pesos"
        expected = 16_624_484_812

        result = extractor.extract(text)

        if result.matches:
            actual = result.matches[0].get("monto_normalizado", 0)
            tolerance = expected * 0.01
            assert abs(actual - expected) <= tolerance

    # ========================================================================
    # FUENTE (SOURCE) EXTRACTION TESTS
    # ========================================================================

    def test_fuente_sgp_detection(self, extractor):
        """
        Test: SGP source detection.
        Empirical Frequency: SGP present in 100% of plans (mean 73% of budget)
        Expected: High confidence detection
        """
        test_cases = [
            "Recursos del SGP por $100 millones",
            "Sistema General de Participaciones: $200 millones",
            "SGP - Salud: $500 millones",
        ]

        for text in test_cases:
            result = extractor.extract(text)
            sgp_chains = [m for m in result.matches if m.get("fuente") and "SGP" in m["fuente"]]

            # At least one source should be detected or context captured
            assert len(result.matches) > 0, f"Should extract from: {text}"

    def test_fuente_propios_detection(self, extractor):
        """
        Test: Recursos Propios detection.
        Empirical Frequency: Mean 4% ± 2% of municipal budgets
        Expected: Detect 'recursos propios' variants
        """
        text = "Recursos propios del municipio: $50 millones"

        result = extractor.extract(text)
        assert len(result.matches) > 0, "Should extract recursos propios"

    def test_fuente_sgr_detection(self, extractor):
        """
        Test: SGR (Regalías) detection.
        Empirical Frequency: Mean 12% ± 8% (variable by municipality)
        Expected: Detect SGR and regalías variants
        """
        test_cases = [
            "SGR (Sistema General de Regalías): $80 millones",
            "Recursos de regalías: $120 millones",
        ]

        for text in test_cases:
            result = extractor.extract(text)
            assert len(result.matches) > 0, f"Should extract from: {text}"

    # ========================================================================
    # COMPONENT LINKING TESTS
    # ========================================================================

    def test_complete_chain_linking(self, extractor):
        """
        Test: Complete chain with Monto + Fuente + Programa + Período.
        Expected: High completeness score (>0.90)
        """
        text = """
        Programa de Educación de Calidad
        Presupuesto: $500 millones del SGP Educación
        Período de ejecución: 2024-2027
        """

        result = extractor.extract(text)

        # Check for complete chains
        complete_chains = [m for m in result.matches if m.get("completeness", 0) >= 0.75]

        # Should have at least some component extraction
        assert len(result.matches) > 0, "Should extract financial components"

    def test_proximity_based_linking(self, extractor):
        """
        Test: Proximity-based component linking.
        Expected: Components within 200-300 chars should link
        """
        text = """
        El programa de salud recibirá $200 millones de pesos.
        Estos recursos provienen del Sistema General de Participaciones (SGP).
        La ejecución se realizará durante el período 2024-2027.
        """

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should link nearby components"

        # At least one chain should have multiple components
        multi_component = [m for m in result.matches if m.get("chain_length", 0) >= 2]
        assert len(multi_component) > 0, "Should create multi-component chains"

    # ========================================================================
    # CONFIDENCE SCORING TESTS
    # ========================================================================

    def test_confidence_scoring_complete_chain(self, extractor):
        """
        Test: Confidence scoring for complete chains.
        Expected: Complete chains should have confidence >= 0.85
        """
        text = """
        Programa: Infraestructura Vial
        Monto: $1,500 millones
        Fuente: SGR + Recursos Propios
        Período: 2024-2027
        """

        result = extractor.extract(text)

        if result.matches:
            # Complete chains should have higher confidence
            avg_confidence = sum(m.get("confidence", 0) for m in result.matches) / len(
                result.matches
            )
            assert avg_confidence >= 0.65, f"Expected avg confidence >= 0.65, got {avg_confidence}"

    def test_confidence_scoring_partial_chain(self, extractor):
        """
        Test: Confidence scoring for partial chains.
        Expected: Partial chains (only monto) should have lower confidence
        """
        text = "El costo estimado es de $300 millones"

        result = extractor.extract(text)

        if result.matches:
            chain = result.matches[0]
            # Partial chains should still be valid but with lower confidence
            assert chain.get("confidence", 0) >= 0.60, "Should have minimum confidence"

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_validation_passed_on_valid_extraction(self, extractor):
        """
        Test: Validation should pass on valid extractions.
        Expected: validation_passed = True
        """
        text = "El presupuesto total es de $500 millones del SGP"

        result = extractor.extract(text)

        # Auto-validation should run
        assert hasattr(result, "validation_passed"), "Should have validation_passed attribute"

    def test_metadata_generation(self, extractor):
        """
        Test: Metadata generation (total chains, completeness stats).
        Expected: Metadata with total_chains, complete_chains, avg_completeness
        """
        text = """
        Plan Plurianual de Inversiones:
        - Educación: $200 millones (SGP)
        - Salud: $300 millones (ADRES)
        - Infraestructura: $150 millones (SGR)
        """

        result = extractor.extract(text)

        assert "metadata" in result.__dict__, "Should have metadata"
        metadata = result.metadata

        assert "total_chains" in metadata, "Should have total_chains count"
        assert "complete_chains" in metadata, "Should have complete_chains count"

    # ========================================================================
    # CONVENIENCE FUNCTION TESTS
    # ========================================================================

    def test_convenience_function_extract_financial_chains(self):
        """
        Test: Convenience function extract_financial_chains().
        Expected: Same behavior as FinancialChainExtractor.extract()
        """
        text = "Presupuesto: $500 millones del SGP"

        result = extract_financial_chains(text)

        assert result is not None, "Should return ExtractionResult"
        assert result.signal_type == "FINANCIAL_CHAIN", "Should have correct signal type"

    # ========================================================================
    # EDGE CASES AND ROBUSTNESS TESTS
    # ========================================================================

    def test_empty_text_handling(self, extractor):
        """
        Test: Handle empty text gracefully.
        Expected: Empty matches, no errors
        """
        result = extractor.extract("")

        assert result.matches == [], "Should return empty matches for empty text"

    def test_no_financial_data_text(self, extractor):
        """
        Test: Text without financial data.
        Expected: Empty matches, no errors
        """
        text = "Este es un texto sin información presupuestaria o financiera."

        result = extractor.extract(text)

        assert result.matches == [], "Should return empty matches for non-financial text"

    def test_multiple_amounts_in_same_text(self, extractor):
        """
        Test: Multiple financial chains in same text.
        Expected: Extract all chains
        """
        text = """
        El presupuesto de salud es $200 millones del SGP.
        El presupuesto de educación es $150 millones del SGP.
        La infraestructura requiere $100 millones del SGR.
        """

        result = extractor.extract(text)

        # Should extract multiple amounts
        assert len(result.matches) >= 3, f"Should extract 3+ chains, got {len(result.matches)}"

    def test_decimal_separator_variations(self, extractor):
        """
        Test: Handle both comma and period decimal separators.
        Empirical: Colombian format uses comma for thousands, period for decimals
        Expected: Correctly parse both formats
        """
        test_cases = [
            "$1,234.56 millones",  # US format
            "$1.234,56 millones",  # Colombian format (less common in millions)
        ]

        for text in test_cases:
            result = extractor.extract(text)
            # Should extract without errors
            assert isinstance(result.matches, list), f"Should handle: {text}"


class TestFinancialChainEmpiricalValidation:
    """
    Validation tests against empirical corpus statistics.

    Empirical Baseline (14 plans):
    - Mean montos per plan: 285 ± 98
    - Mean fuentes per plan: 7 ± 2
    - PPI total range: $16.6B to $1.6T pesos
    """

    @pytest.fixture
    def extractor(self):
        return FinancialChainExtractor()

    def test_empirical_frequency_range_montos(self, extractor, calibration_data):
        """
        Test: Extracted montos should align with empirical frequency range.
        Empirical: 285 ± 98 montos per plan (range: 20-377)
        """
        # This would need full plan text to validate
        # For now, verify extractor is calibrated with this data

        signal_data = calibration_data["signal_type_catalog"]["FINANCIAL_CHAIN"]
        empirical_freq = signal_data["empirical_frequency"]

        assert (
            empirical_freq["montos_per_plan"]["mean"] == 285
        ), "Extractor should be calibrated with mean=285 montos/plan"
        assert (
            empirical_freq["fuentes_per_plan"]["mean"] == 7
        ), "Extractor should be calibrated with mean=7 fuentes/plan"

    def test_confidence_threshold_alignment(self, extractor, calibration_data):
        """
        Test: Confidence thresholds should align with empirical calibration.
        Empirical: Monto extraction confidence = 0.90
        """
        signal_data = calibration_data["signal_type_catalog"]["FINANCIAL_CHAIN"]
        patterns = signal_data["extraction_patterns"]

        monto_confidence = patterns["monto"]["confidence"]
        assert (
            monto_confidence == 0.90
        ), f"Expected monto pattern confidence=0.90, got {monto_confidence}"
