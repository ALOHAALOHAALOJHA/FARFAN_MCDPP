# tests/test_sisas/test_signals.py

import pytest
from datetime import datetime

from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.core.signal import (
    SignalContext, SignalSource, SignalCategory, SignalConfidence
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types.structural import (
    StructuralAlignmentSignal, AlignmentStatus,
    SchemaConflictSignal, CanonicalMappingSignal
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types.epistemic import (
    AnswerDeterminacySignal, DeterminacyLevel,
    AnswerSpecificitySignal, SpecificityLevel,
    EmpiricalSupportSignal, EmpiricalSupportLevel
)
from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signals.types.contrast import (
    DecisionDivergenceSignal, DivergenceType, DivergenceSeverity
)


@pytest.fixture
def sample_context():
    return SignalContext(
        node_type="question",
        node_id="Q147",
        phase="phase_00",
        consumer_scope="Phase_00"
    )


@pytest.fixture
def sample_source():
    return SignalSource(
        event_id="evt-test-123",
        source_file="Q147.json",
        source_path="dimensions/DIM06/questions/Q147.json",
        generation_timestamp=datetime.utcnow(),
        generator_vehicle="signal_context_scoper"
    )


class TestStructuralSignals:
    """Tests para señales estructurales"""
    
    def test_structural_alignment_signal(self, sample_context, sample_source):
        signal = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="dimensions/DIM06/questions/Q147",
            actual_path="dimensions/DIM06/questions/Q147.json",
            missing_elements=[],
            extra_elements=[]
        )
        
        assert signal.signal_type == "StructuralAlignmentSignal"
        assert signal.category == SignalCategory.STRUCTURAL
        assert signal.alignment_status == AlignmentStatus.ALIGNED
        assert signal.compute_alignment_score() == 1.0
    
    def test_alignment_score_partial(self, sample_context, sample_source):
        signal = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.PARTIAL,
            canonical_path="test",
            actual_path="test",
            missing_elements=["field1"],
            extra_elements=["field2"]
        )
        
        score = signal.compute_alignment_score()
        assert 0 < score < 1.0
    
    def test_canonical_mapping_signal(self, sample_context, sample_source):
        signal = CanonicalMappingSignal(
            context=sample_context,
            source=sample_source,
            source_item_id="Q147",
            mapped_entities={
                "policy_area": "PA03",
                "dimension": "DIM06",
                "cluster": "CL01"
            },
            unmapped_aspects=[],
            mapping_completeness=1.0
        )
        
        assert signal.signal_type == "CanonicalMappingSignal"
        assert signal.mapped_entities["policy_area"] == "PA03"


class TestEpistemicSignals:
    """Tests para señales epistémicas"""
    
    def test_determinacy_signal_high(self, sample_context, sample_source):
        signal = AnswerDeterminacySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            determinacy_level=DeterminacyLevel.HIGH,
            affirmative_markers=["sí", "existe", "cuenta con"],
            ambiguity_markers=[],
            negation_markers=[]
        )
        
        assert signal.signal_type == "AnswerDeterminacySignal"
        assert signal.category == SignalCategory.EPISTEMIC
        assert signal.determinacy_level == DeterminacyLevel.HIGH
    
    def test_determinacy_signal_medium(self, sample_context, sample_source):
        signal = AnswerDeterminacySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            determinacy_level=DeterminacyLevel.MEDIUM,
            affirmative_markers=["sí"],
            ambiguity_markers=["en algunos casos"],
            negation_markers=[]
        )
        
        assert signal.determinacy_level == DeterminacyLevel.MEDIUM
        assert "en algunos casos" in signal.ambiguity_markers
    
    def test_specificity_signal(self, sample_context, sample_source):
        signal = AnswerSpecificitySignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            specificity_level=SpecificityLevel.LOW,
            expected_elements=["formal_instrument", "institutional_owner", "mandatory_scope"],
            found_elements=["institutional_owner"],
            missing_elements=["formal_instrument", "mandatory_scope"],
            specificity_score=0.33
        )
        
        assert signal.signal_type == "AnswerSpecificitySignal"
        assert signal.specificity_level == SpecificityLevel.LOW
        assert len(signal.missing_elements) == 2
    
    def test_empirical_support_signal(self, sample_context, sample_source):
        signal = EmpiricalSupportSignal(
            context=sample_context,
            source=sample_source,
            question_id="Q147",
            support_level=EmpiricalSupportLevel.MODERATE,
            normative_references=["Ley 1448 de 2011"],
            document_references=[],
            institutional_references=["Unidad de Víctimas"]
        )
        
        assert signal.signal_type == "EmpiricalSupportSignal"
        assert signal.support_level == EmpiricalSupportLevel.MODERATE
        assert "Ley 1448 de 2011" in signal.normative_references


class TestContrastSignals: 
    """Tests para señales de contraste"""
    
    def test_decision_divergence_signal(self, sample_context, sample_source):
        signal = DecisionDivergenceSignal(
            context=sample_context,
            source=sample_source,
            item_id="Q147",
            legacy_value="COMPLIANT",
            legacy_source="legacy_system_v1",
            signal_based_value="INDETERMINATE",
            supporting_signals=["AnswerDeterminacySignal", "EmpiricalSupportSignal"],
            divergence_type=DivergenceType.CLASSIFICATION_MISMATCH,
            divergence_severity=DivergenceSeverity.HIGH
        )
        
        assert signal.signal_type == "DecisionDivergenceSignal"
        assert signal.category == SignalCategory.CONTRAST
        assert signal.legacy_value != signal.signal_based_value
        assert signal.divergence_severity == DivergenceSeverity.HIGH


class TestSignalDeterminism:
    """Tests para el axioma: deterministic (mismo input → misma señal)"""
    
    def test_same_input_same_hash(self, sample_context, sample_source):
        """El mismo input debe producir el mismo hash"""
        signal1 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="test/path",
            actual_path="test/path"
        )
        
        signal2 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="test/path",
            actual_path="test/path"
        )
        
        # Los hashes deben ser idénticos
        assert signal1.compute_hash() == signal2.compute_hash()
    
    def test_different_input_different_hash(self, sample_context, sample_source):
        """Diferente input debe producir diferente hash"""
        signal1 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.ALIGNED,
            canonical_path="test/path1",
            actual_path="test/path1"
        )
        
        signal2 = StructuralAlignmentSignal(
            context=sample_context,
            source=sample_source,
            alignment_status=AlignmentStatus.MISALIGNED,  # Diferente
            canonical_path="test/path2",
            actual_path="test/path2"
        )
        
        assert signal1.compute_hash() != signal2.compute_hash()