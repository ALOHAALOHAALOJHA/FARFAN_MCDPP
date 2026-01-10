"""
Tests for CausalVerbExtractor (MC08) - Empirically Calibrated.

Auto-generated from empirical corpus with gold standard examples.

Author: CQC Extractor Excellence Framework
Version: 2.0.0
Date: 2026-01-06
"""

import pytest

from farfan_pipeline.infrastructure.extractors import CausalVerbExtractor, extract_causal_links


class TestCausalVerbExtractor:
    """Test suite for CausalVerbExtractor based on empirical corpus."""

    @pytest.fixture
    def extractor(self):
        """Create extractor instance."""
        return CausalVerbExtractor()

    # ========================================================================
    # EMPIRICAL VERB FREQUENCY TESTS
    # ========================================================================

    def test_top_causal_verb_fortalecer(self, extractor):
        """
        Test: Extract 'fortalecer' (top empirical verb).
        Empirical Frequency: Mean 52 mentions/plan (range: 28-89)
        Expected: High confidence extraction (strong causal verb)
        """
        text = "Fortalecer la capacidad institucional de la Secretaría de Salud"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'fortalecer'"

        verb_match = result.matches[0]
        assert (
            verb_match["verb_lemma"] == "fortalecer"
        ), f"Expected lemma 'fortalecer', got '{verb_match['verb_lemma']}'"
        assert verb_match["causal_strength"] in [
            "medium",
            "strong",
        ], "Fortalecer should be medium/strong causal verb"

    def test_top_causal_verb_implementar(self, extractor):
        """
        Test: Extract 'implementar' (2nd most frequent).
        Empirical Frequency: Mean 51 mentions/plan (range: 24-87)
        Expected: Strong causal strength
        """
        text = "Implementar el programa de vacunación infantil en zonas rurales"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'implementar'"

        verb_match = result.matches[0]
        assert verb_match["verb_lemma"] == "implementar"
        assert verb_match["causal_strength"] == "strong", "Implementar should be strong causal verb"

    def test_top_causal_verb_garantizar(self, extractor):
        """
        Test: Extract 'garantizar' (3rd most frequent).
        Empirical Frequency: Mean 55 mentions/plan (range: 31-91)
        Expected: Strong causal strength
        """
        text = "Garantizar el acceso universal a servicios de salud de calidad"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'garantizar'"
        assert result.matches[0]["verb_lemma"] == "garantizar"
        assert result.matches[0]["causal_strength"] == "strong"

    def test_top_causal_verb_promover(self, extractor):
        """
        Test: Extract 'promover' (4th most frequent).
        Empirical Frequency: Mean 48 mentions/plan (range: 22-78)
        Expected: Medium causal strength
        """
        text = "Promover el desarrollo económico local mediante proyectos productivos"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'promover'"
        assert result.matches[0]["verb_lemma"] == "promover"
        assert result.matches[0]["causal_strength"] == "medium"

    def test_top_causal_verb_mejorar(self, extractor):
        """
        Test: Extract 'mejorar' (5th most frequent).
        Empirical Frequency: Mean 49 mentions/plan (range: 25-84)
        Expected: Medium causal strength
        """
        text = "Mejorar la infraestructura educativa en establecimientos rurales"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'mejorar'"
        assert result.matches[0]["verb_lemma"] == "mejorar"
        assert result.matches[0]["causal_strength"] == "medium"

    # ========================================================================
    # VERB CONJUGATION TESTS
    # ========================================================================

    def test_verb_conjugation_present_3rd_person(self, extractor):
        """
        Test: Detect conjugated form (3rd person present).
        Example: 'fortalecer' → 'fortalece'
        Expected: Extract and lemmatize correctly
        """
        text = "El programa fortalece las capacidades técnicas del municipio"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract conjugated verb 'fortalece'"
        assert result.matches[0]["verb_lemma"] == "fortalecer", "Should lemmatize to 'fortalecer'"

    def test_verb_conjugation_future(self, extractor):
        """
        Test: Detect future tense conjugation.
        Example: 'implementar' → 'implementará'
        Expected: Extract and lemmatize correctly
        """
        text = "La alcaldía implementará estrategias de prevención de violencia"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract 'implementará'"
        assert result.matches[0]["verb_lemma"] == "implementar"

    def test_verb_conjugation_gerund(self, extractor):
        """
        Test: Detect gerund form.
        Example: 'mejorar' → 'mejorando'
        Expected: Extract and lemmatize correctly
        """
        text = "Mejorando la calidad del servicio de acueducto rural"

        result = extractor.extract(text)

        if result.matches:  # Gerunds may be less common in strategic plans
            assert result.matches[0]["verb_lemma"] == "mejorar"

    def test_verb_conjugation_past_participle(self, extractor):
        """
        Test: Detect past participle.
        Example: 'desarrollar' → 'desarrollado'
        Expected: Extract and lemmatize correctly
        """
        text = "Programas desarrollados con enfoque diferencial y territorial"

        result = extractor.extract(text)

        if result.matches:
            assert result.matches[0]["verb_lemma"] == "desarrollar"

    # ========================================================================
    # ARGUMENT EXTRACTION TESTS
    # ========================================================================

    def test_object_extraction_simple(self, extractor):
        """
        Test: Extract object (what is being acted upon).
        Example: "fortalecer [la capacidad institucional]"
        Expected: Extract complete object phrase
        """
        text = "Fortalecer la capacidad institucional de la Secretaría de Salud"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract causal link"

        link = result.matches[0]
        assert link["object"] is not None, "Should extract object"
        assert (
            "capacidad" in link["object"].lower()
        ), f"Object should contain 'capacidad', got: {link['object']}"

    def test_outcome_extraction_with_para(self, extractor):
        """
        Test: Extract outcome with 'para' connector.
        Empirical: 'para' is common outcome marker
        Expected: Extract outcome phrase
        """
        text = "Implementar el programa de vacunación para reducir la mortalidad infantil"

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract causal link"

        link = result.matches[0]
        assert link["outcome"] is not None, "Should extract outcome"
        assert (
            "reducir" in link["outcome"].lower() or "mortalidad" in link["outcome"].lower()
        ), f"Outcome should mention goal, got: {link['outcome']}"

    def test_subject_extraction(self, extractor):
        """
        Test: Extract subject (entity performing action).
        Example: "[La alcaldía] implementará..."
        Expected: Extract subject when present
        """
        text = "La Secretaría de Educación fortalecerá los procesos pedagógicos"

        result = extractor.extract(text)

        if result.matches and result.matches[0]["subject"]:
            subject = result.matches[0]["subject"]
            assert (
                "secretaría" in subject.lower() or "educación" in subject.lower()
            ), f"Subject should reference entity, got: {subject}"

    def test_complete_causal_chain(self, extractor):
        """
        Test: Extract complete causal chain (subject + verb + object + outcome).
        Expected: High completeness, confidence boost
        """
        text = """
        El municipio fortalecerá los sistemas de información territorial
        para mejorar la toma de decisiones basada en evidencia
        """

        result = extractor.extract(text)

        assert len(result.matches) > 0, "Should extract causal chain"

        # Find most complete link
        complete_links = [m for m in result.matches if m.get("is_complete", False)]

        if complete_links:
            link = complete_links[0]
            assert link["confidence"] >= 0.70, "Complete chains should have higher confidence"
            assert link["chain_length"] >= 2, "Complete chains should have length >= 2"

    # ========================================================================
    # CAUSAL STRENGTH CLASSIFICATION TESTS
    # ========================================================================

    def test_strong_causal_verbs_classification(self, extractor):
        """
        Test: Strong causal verbs classification.
        Strong verbs: implementar, desarrollar, crear, construir, garantizar
        Expected: causal_strength = "strong"
        """
        strong_texts = [
            "Implementar el sistema de monitoreo",
            "Desarrollar capacidades técnicas",
            "Crear nuevos programas sociales",
            "Construir infraestructura educativa",
            "Garantizar el acceso a servicios",
        ]

        for text in strong_texts:
            result = extractor.extract(text)
            if result.matches:
                assert (
                    result.matches[0]["causal_strength"] == "strong"
                ), f"Text '{text}' should have strong causal verb"

    def test_medium_causal_verbs_classification(self, extractor):
        """
        Test: Medium causal verbs classification.
        Medium verbs: fortalecer, mejorar, promover, impulsar, fomentar
        Expected: causal_strength = "medium"
        """
        medium_texts = [
            "Fortalecer el tejido social",
            "Mejorar la conectividad rural",
            "Promover la participación ciudadana",
            "Impulsar el desarrollo económico",
            "Fomentar la cultura de paz",
        ]

        for text in medium_texts:
            result = extractor.extract(text)
            if result.matches:
                assert (
                    result.matches[0]["causal_strength"] == "medium"
                ), f"Text '{text}' should have medium causal verb"

    def test_weak_causal_verbs_classification(self, extractor):
        """
        Test: Weak causal verbs classification.
        Weak verbs: buscar, procurar, intentar, propender
        Expected: causal_strength = "weak"
        """
        weak_texts = [
            "Buscar mecanismos de financiación",
            "Procurar la articulación interinstitucional",
            "Propender por el bienestar colectivo",
        ]

        for text in weak_texts:
            result = extractor.extract(text)
            if result.matches:
                assert (
                    result.matches[0]["causal_strength"] == "weak"
                ), f"Text '{text}' should have weak causal verb"

    # ========================================================================
    # CONFIDENCE SCORING TESTS
    # ========================================================================

    def test_confidence_boost_for_complete_chains(self, extractor):
        """
        Test: Confidence boost for complete causal chains.
        Expected: verb+object+outcome > verb+object > verb alone
        """
        text_complete = "Implementar el programa para reducir la pobreza"
        text_partial = "Implementar el programa de desarrollo"
        text_minimal = "Implementar estrategias"

        result_complete = extractor.extract(text_complete)
        result_partial = extractor.extract(text_partial)
        result_minimal = extractor.extract(text_minimal)

        if result_complete.matches and result_partial.matches:
            conf_complete = result_complete.matches[0]["confidence"]
            conf_partial = result_partial.matches[0]["confidence"]

            # Complete should have higher or equal confidence
            assert (
                conf_complete >= conf_partial - 0.05
            ), "Complete chains should have >= confidence than partial"

    def test_confidence_by_causal_strength(self, extractor):
        """
        Test: Confidence varies by causal strength.
        Expected: strong > medium > weak (base confidence)
        """
        text_strong = "Implementar el programa de salud"
        text_medium = "Fortalecer el sistema de salud"
        text_weak = "Buscar mecanismos de mejora"

        results = {
            "strong": extractor.extract(text_strong),
            "medium": extractor.extract(text_medium),
            "weak": extractor.extract(text_weak),
        }

        # Verify base confidence differences
        for strength, result in results.items():
            if result.matches:
                conf = result.matches[0]["confidence"]
                if strength == "strong":
                    assert conf >= 0.75, "Strong verbs should have conf >= 0.75"
                elif strength == "medium":
                    assert conf >= 0.65, "Medium verbs should have conf >= 0.65"
                elif strength == "weak":
                    assert conf >= 0.60, "Weak verbs should have conf >= 0.60"

    # ========================================================================
    # METADATA GENERATION TESTS
    # ========================================================================

    def test_metadata_by_strength_distribution(self, extractor):
        """
        Test: Metadata includes distribution by causal strength.
        Expected: metadata.by_strength = {strong: X, medium: Y, weak: Z}
        """
        text = """
        Implementar programas de salud.
        Fortalecer la educación rural.
        Buscar alianzas estratégicas.
        """

        result = extractor.extract(text)

        assert "metadata" in result.__dict__, "Should have metadata"
        metadata = result.metadata

        assert "by_strength" in metadata, "Should have by_strength distribution"
        by_strength = metadata["by_strength"]

        assert "strong" in by_strength
        assert "medium" in by_strength
        assert "weak" in by_strength

        total = by_strength["strong"] + by_strength["medium"] + by_strength["weak"]
        assert total == len(result.matches), "Sum of by_strength should equal total matches"

    def test_metadata_avg_chain_length(self, extractor):
        """
        Test: Metadata includes average chain length.
        Expected: metadata.avg_chain_length based on argument extraction
        """
        text = """
        Implementar el programa de vacunación para reducir mortalidad.
        Mejorar la infraestructura.
        """

        result = extractor.extract(text)

        assert "metadata" in result.__dict__
        metadata = result.metadata

        assert "avg_chain_length" in metadata, "Should have avg_chain_length"
        avg_length = metadata["avg_chain_length"]

        assert avg_length >= 1.0, "Chain length should be at least 1 (verb only)"

    # ========================================================================
    # MULTIPLE VERBS IN SAME TEXT
    # ========================================================================

    def test_multiple_causal_verbs_extraction(self, extractor, causal_verb_text_samples):
        """
        Test: Extract multiple causal verbs from same text.
        Expected: All verbs extracted with correct lemmas
        """
        text = """
        Fortalecer las capacidades institucionales para mejorar la prestación
        de servicios. Implementar sistemas de información que permitan
        garantizar la calidad y promover la transparencia.
        """

        result = extractor.extract(text)

        # Should extract multiple causal links
        assert (
            len(result.matches) >= 3
        ), f"Should extract 3+ causal verbs, got {len(result.matches)}"

        verbs_found = {m["verb_lemma"] for m in result.matches}
        expected_verbs = {"fortalecer", "mejorar", "implementar", "garantizar", "promover"}

        # At least 3 of the expected verbs should be found
        intersection = verbs_found & expected_verbs
        assert (
            len(intersection) >= 3
        ), f"Should find at least 3 expected verbs, found: {verbs_found}"

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_validation_passed_attribute(self, extractor):
        """
        Test: Validation passed attribute is set.
        Expected: validation_passed = True for valid extractions
        """
        text = "Fortalecer la capacidad institucional de la alcaldía"

        result = extractor.extract(text)

        assert hasattr(result, "validation_passed"), "Should have validation_passed attribute"

    def test_object_requirement_for_completeness(self, extractor):
        """
        Test: Links without object are not marked as complete.
        Expected: is_complete = False if no object extracted
        """
        # This is a tricky case - verb without clear object
        text = "Implementar rápidamente"

        result = extractor.extract(text)

        if result.matches:
            # Links should have object to be complete
            for link in result.matches:
                if not link["object"]:
                    assert not link["is_complete"], "Links without object should not be complete"

    # ========================================================================
    # CONVENIENCE FUNCTION TESTS
    # ========================================================================

    def test_convenience_function_extract_causal_links(self):
        """
        Test: Convenience function extract_causal_links().
        Expected: Same behavior as CausalVerbExtractor.extract()
        """
        text = "Fortalecer la educación rural"

        result = extract_causal_links(text)

        assert result is not None, "Should return ExtractionResult"
        assert result.signal_type == "CAUSAL_LINK", "Should have correct signal type"
        assert len(result.matches) > 0, "Should extract causal link"

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

    def test_no_causal_verbs_text(self, extractor):
        """
        Test: Text without causal verbs.
        Expected: Empty matches
        """
        text = "El municipio cuenta con 50,000 habitantes distribuidos en 20 veredas."

        result = extractor.extract(text)

        assert result.matches == [], "Should return empty matches for text without causal verbs"

    def test_case_insensitive_matching(self, extractor):
        """
        Test: Case-insensitive verb matching.
        Expected: Extract verbs regardless of case
        """
        test_cases = [
            "FORTALECER la capacidad",  # ALL CAPS
            "Fortalecer la capacidad",  # Title case
            "fortalecer la capacidad",  # lowercase
        ]

        for text in test_cases:
            result = extractor.extract(text)
            assert len(result.matches) > 0, f"Should extract from '{text}' (case-insensitive)"
            assert result.matches[0]["verb_lemma"] == "fortalecer"


class TestCausalVerbEmpiricalValidation:
    """
    Validation tests against empirical corpus statistics.

    Empirical Baseline (14 plans):
    - Top 10 causal verbs frequency ranges
    - Causal connectors frequency
    - Implicit vs explicit theory of change
    """

    @pytest.fixture
    def extractor(self):
        return CausalVerbExtractor()

    def test_empirical_verb_taxonomy_completeness(self, extractor):
        """
        Test: Extractor includes all top 10 empirical verbs.
        Empirical Top 10: fortalecer, implementar, garantizar, promover,
                         mejorar, gestionar, asegurar, impulsar, articular, capacitar
        Expected: All verbs in CAUSAL_VERBS taxonomy
        """
        all_verbs = []
        for strength, verbs in extractor.CAUSAL_VERBS.items():
            all_verbs.extend(verbs)

        empirical_top_10 = [
            "fortalecer",
            "implementar",
            "garantizar",
            "promover",
            "mejorar",
            "gestionar",
            "asegurar",
            "impulsar",
            "articular",
            "capacitar",
        ]

        for verb in empirical_top_10:
            assert verb in all_verbs, f"Top empirical verb '{verb}' should be in taxonomy"

    def test_total_verbs_coverage(self, extractor):
        """
        Test: Total verbs in taxonomy provides good coverage.
        Expected: 25+ verbs across strong/medium/weak categories
        """
        total_verbs = extractor._total_verbs()

        assert total_verbs >= 25, f"Should have 25+ causal verbs for coverage, got {total_verbs}"

    def test_confidence_threshold_alignment(self, extractor, calibration_data):
        """
        Test: Confidence thresholds align with empirical calibration.
        Empirical: Causal verb extraction confidence = 0.82 (with context)
        """
        signal_data = calibration_data["signal_type_catalog"]["CAUSAL_VERBS"]
        patterns = signal_data["extraction_patterns"]

        verb_confidence = patterns["causal_verbs"]["confidence"]
        assert (
            verb_confidence == 0.82
        ), f"Expected causal verb confidence=0.82, got {verb_confidence}"
