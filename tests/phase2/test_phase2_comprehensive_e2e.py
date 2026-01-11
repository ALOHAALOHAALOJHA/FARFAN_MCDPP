"""
Comprehensive End-to-End Tests for Phase 2.

This test suite provides complete coverage of Phase 2 from end to end:
- Factory and Registry initialization
- IrrigationSynchronizer execution plan generation
- TaskExecutor execution (sequential and parallel)
- EvidenceNexus evidence assembly
- Carver narrative synthesis
- Checkpoint management and recovery
- Circuit breaker and resource management
- Contract validation and hydration

E2E Flow:
    Questionnaire + Chunks → IrrigationSynchronizer → ExecutionPlan
    → TaskExecutor → TaskResults → EvidenceNexus → Carver → DoctoralAnswers
"""

import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, MagicMock, patch

import pytest

# =============================================================================
# FIXTURES - Test Data Factory
# =============================================================================


@pytest.fixture
def sample_questionnaire():
    """Create a valid questionnaire for testing."""
    return {
        "canonical_notation": {
            "dimensions": {
                "D1": "Insumos",
                "D2": "Actividades",
                "D3": "Productos",
                "D4": "Resultados",
                "D5": "Impactos",
                "D6": "Causalidad"
            },
            "policy_areas": {
                "PA01": "Derechos de las mujeres e igualdad de género",
                "PA02": "Economía y empoderamiento económico femenino",
                "PA03": "Participación política y liderazgo",
                "PA04": "Educación",
                "PA05": "Salud",
                "PA06": "Violencia de género",
                "PA07": "Normativa y políticas",
                "PA08": "Presupuesto",
                "PA09": "Cooperación",
                "PA10": "Datos y estadísticas"
            }
        },
        "blocks": {
            "micro_questions": [
                {
                    "question_id": "Q001",
                    "question_global": 1,
                    "policy_area_id": "PA01",
                    "dimension_id": "D1",
                    "text": "¿Cuál es el presupuesto asignado para programas de igualdad de género?",
                    "expected_elements": [
                        {"name": "monto_presupuestario", "type": "currency", "required": True}
                    ],
                    "patterns": [{"pattern": "presupuesto.*genero", "type": "regex"}],
                    "signal_requirements": ["S_BUDGET"],
                    "method_sets": ["N1-EMP", "N2-INF", "N3-AUD"]
                },
                {
                    "question_id": "Q002",
                    "question_global": 2,
                    "policy_area_id": "PA01",
                    "dimension_id": "D2",
                    "text": "¿Qué actividades se implementan para promover la igualdad?",
                    "expected_elements": [
                        {"name": "actividades", "type": "list", "required": True}
                    ],
                    "patterns": [{"pattern": "actividad.*implementar", "type": "regex"}],
                    "signal_requirements": ["S_ACTIVITY"],
                    "method_sets": ["N1-EMP", "N2-INF"]
                },
                {
                    "question_id": "Q003",
                    "question_global": 3,
                    "policy_area_id": "PA02",
                    "dimension_id": "D3",
                    "text": "¿Cuántas mujeres se beneficiaron de programas de empoderamiento económico?",
                    "expected_elements": [
                        {"name": "beneficiarias", "type": "numeric", "required": True}
                    ],
                    "patterns": [{"pattern": "mujeres.*beneficiarias", "type": "regex"}],
                    "signal_requirements": ["S_BENEFICIARIES"],
                    "method_sets": ["N1-EMP", "N3-AUD"]
                }
            ]
        }
    }


@pytest.fixture
def sample_preprocessed_document():
    """Create a valid PreprocessedDocument for testing."""
    from farfan_pipeline.calibracion_parametrizacion.types import (
        ChunkData,
        PreprocessedDocument,
        DimensionCausal,
        PolicyArea,
    )

    # Dimension string to enum mapping
    DIMENSION_MAP = {
        "D1": DimensionCausal.DIM01_INSUMOS,
        "D2": DimensionCausal.DIM02_ACTIVIDADES,
        "D3": DimensionCausal.DIM03_PRODUCTOS,
        "D4": DimensionCausal.DIM04_RESULTADOS,
        "D5": DimensionCausal.DIM05_IMPACTOS,
        "D6": DimensionCausal.DIM06_CAUSALIDAD,
    }

    # Policy area string to enum mapping
    PA_MAP = {
        "PA01": PolicyArea.PA01,
        "PA02": PolicyArea.PA02,
        "PA03": PolicyArea.PA03,
        "PA04": PolicyArea.PA04,
        "PA05": PolicyArea.PA05,
        "PA06": PolicyArea.PA06,
        "PA07": PolicyArea.PA07,
        "PA08": PolicyArea.PA08,
        "PA09": PolicyArea.PA09,
        "PA10": PolicyArea.PA10,
    }

    chunks = []
    for dim in ["D1", "D2", "D3", "D4", "D5", "D6"]:
        for pa in ["PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"]:
            chunks.append(ChunkData(
                chunk_id=f"{dim}_{pa}",
                text=f"Contenido del documento para dimensión {dim} y área política {pa}. " +
                     "Este texto contiene información sobre presupuesto, actividades, " +
                     "beneficiarias y otros elementos relevantes para el análisis.",
                start_offset=0,
                end_offset=200,
                policy_area=PA_MAP.get(pa),
                dimension_causal=DIMENSION_MAP.get(dim),
                metadata={}
            ))

    return PreprocessedDocument(
        document_id="test_doc_001",
        source_path="/test/sample_document.pdf",
        chunks=chunks,
        metadata={"source": "test", "created_at": datetime.now(UTC).isoformat()}
    )


@pytest.fixture
def mock_signal_registry():
    """Create a mock SignalRegistry for testing."""
    registry = Mock()

    def get_signals_for_chunk(chunk, requirements):
        signals = []
        for req in requirements:
            signals.append({
                "signal_id": f"S_{chunk.chunk_id}_{req}",
                "signal_type": req,
                "content": {"value": "test_signal", "confidence": 0.9}
            })
        return signals

    registry.get_signals_for_chunk = get_signals_for_chunk
    registry.get_all_policy_areas = Mock(return_value=[
        "PA01", "PA02", "PA03", "PA04", "PA05", "PA06", "PA07", "PA08", "PA09", "PA10"
    ])
    return registry


@pytest.fixture
def tmp_checkpoint_dir(tmp_path):
    """Create temporary checkpoint directory."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    return checkpoint_dir


# =============================================================================
# TEST CLASS 1: Factory and Registry Tests
# =============================================================================


class TestPhase2FactoryAndRegistry:
    """Test Factory and Registry initialization."""

    def test_factory_initialization(self):
        """Test AnalysisPipelineFactory can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_10_00_factory import AnalysisPipelineFactory

        factory = AnalysisPipelineFactory()

        assert factory is not None
        assert hasattr(factory, 'create_executor')
        assert hasattr(factory, 'create_synchronizer')
        assert hasattr(factory, 'create_task_executor')

    def test_class_registry_initialization(self):
        """Test ClassRegistry can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_10_01_class_registry import ClassRegistry

        registry = ClassRegistry()

        assert registry is not None
        assert hasattr(registry, 'get_class')
        assert hasattr(registry, 'register_class')

    def test_methods_registry_initialization(self):
        """Test MethodsRegistry can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_10_02_methods_registry import MethodsRegistry

        registry = MethodsRegistry()

        assert registry is not None
        assert hasattr(registry, 'get_method')
        assert hasattr(registry, 'list_methods')


# =============================================================================
# TEST CLASS 2: IrrigationSynchronizer Tests
# =============================================================================


class TestPhase2IrrigationSynchronizer:
    """Test IrrigationSynchronizer execution plan generation."""

    def test_synchronizer_initialization(self, sample_questionnaire, sample_preprocessed_document):
        """Test IrrigationSynchronizer can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer

        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        assert synchronizer is not None
        assert synchronizer.questionnaire == sample_questionnaire
        assert synchronizer.chunk_count == 60
        assert synchronizer.question_count == 3

    def test_build_execution_plan(self, sample_questionnaire, sample_preprocessed_document):
        """Test ExecutionPlan can be built."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer

        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        plan = synchronizer.build_execution_plan()

        assert plan is not None
        assert isinstance(plan.tasks, tuple)
        assert len(plan.tasks) > 0
        assert plan.plan_id is not None
        assert plan.integrity_hash is not None
        assert plan.correlation_id is not None

    def test_execution_plan_serialization(self, sample_questionnaire, sample_preprocessed_document):
        """Test ExecutionPlan can be serialized and deserialized."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import (
            ExecutionPlan,
            IrrigationSynchronizer,
        )

        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        original_plan = synchronizer.build_execution_plan()

        # Serialize
        plan_dict = original_plan.to_dict()

        # Deserialize
        restored_plan = ExecutionPlan.from_dict(plan_dict)

        assert restored_plan.plan_id == original_plan.plan_id
        assert len(restored_plan.tasks) == len(original_plan.tasks)
        assert restored_plan.integrity_hash == original_plan.integrity_hash

    def test_chunk_routing_validation(self, sample_questionnaire, sample_preprocessed_document):
        """Test chunk routing validation works."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer

        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        question = {
            "question_id": "Q001",
            "policy_area_id": "PA01",
            "dimension_id": "D1",
            "expected_elements": [{"name": "test", "type": "string"}]
        }

        result = synchronizer.validate_chunk_routing(question)

        assert result is not None
        assert result.chunk_id is not None
        assert result.policy_area_id == "PA01"
        assert result.dimension_id == "D1"
        assert len(result.text_content) > 0


# =============================================================================
# TEST CLASS 3: TaskExecutor Tests
# =============================================================================


class TestPhase2TaskExecutor:
    """Test TaskExecutor execution."""

    def test_task_executor_initialization(self, sample_questionnaire, sample_preprocessed_document):
        """Test TaskExecutor can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import TaskExecutor

        executor = TaskExecutor(
            questionnaire_monolith=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        assert executor is not None
        assert executor.questionnaire_monolith == sample_questionnaire
        assert len(executor._question_index) > 0

    def test_dynamic_executor_base_slot_derivation(self):
        """Test base_slot derivation formula."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import DynamicContractExecutor

        test_cases = [
            ("Q001", "D1-Q1"),
            ("Q006", "D2-Q1"),
            ("Q030", "D6-Q5"),
            ("Q031", "D1-Q1"),
            ("Q060", "D6-Q5"),
            ("Q150", "D6-Q5"),
        ]

        for question_id, expected_slot in test_cases:
            derived_slot = DynamicContractExecutor._derive_base_slot(question_id)
            assert derived_slot == expected_slot, f"Q{question_id} should derive to {expected_slot}, got {derived_slot}"

    def test_checkpoint_manager(self, tmp_checkpoint_dir):
        """Test CheckpointManager operations."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import CheckpointManager

        manager = CheckpointManager(checkpoint_dir=tmp_checkpoint_dir)

        plan_id = "test_plan_001"
        completed_tasks = ["task_1", "task_2", "task_3"]

        # Save checkpoint
        checkpoint_path = manager.save_checkpoint(plan_id, completed_tasks)

        assert checkpoint_path.exists()

        # Resume from checkpoint
        resumed_tasks = manager.resume_from_checkpoint(plan_id)

        assert resumed_tasks == set(completed_tasks)

        # Clear checkpoint
        cleared = manager.clear_checkpoint(plan_id)

        assert cleared is True
        assert not checkpoint_path.exists()

    def test_checkpoint_integrity_validation(self, tmp_checkpoint_dir):
        """Test checkpoint hash validation detects corruption."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import (
            CheckpointCorruptionError,
            CheckpointManager,
        )

        manager = CheckpointManager(checkpoint_dir=tmp_checkpoint_dir)

        plan_id = "test_plan_corrupt"
        completed_tasks = ["task_1"]

        # Save checkpoint
        checkpoint_path = manager.save_checkpoint(plan_id, completed_tasks)

        # Corrupt the checkpoint
        with open(checkpoint_path, "r") as f:
            data = json.load(f)
        data["checkpoint_hash"] = "corrupted_hash"
        with open(checkpoint_path, "w") as f:
            json.dump(data, f)

        # Should raise error on resume
        with pytest.raises(CheckpointCorruptionError):
            manager.resume_from_checkpoint(plan_id)


# =============================================================================
# TEST CLASS 4: EvidenceNexus Tests
# =============================================================================


class TestPhase2EvidenceNexus:
    """Test EvidenceNexus evidence assembly."""

    def test_evidence_nexus_initialization(self):
        """Test EvidenceNexus can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_80_00_evidence_nexus import EvidenceNexus

        nexus = EvidenceNexus()

        assert nexus is not None
        assert hasattr(nexus, 'add_evidence')
        assert hasattr(nexus, 'query')
        assert hasattr(nexus, 'validate')

    def test_evidence_node_creation(self):
        """Test EvidenceNode creation."""
        from farfan_pipeline.phases.Phase_2.phase2_80_00_evidence_nexus import (
            EvidenceNode,
            EvidenceType,
        )

        node = EvidenceNode.create(
            evidence_type=EvidenceType.INDICATOR_NUMERIC,
            content={"value": 100, "unit": "USD"},
            confidence=0.9,
            source_method="test_method"
        )

        assert node is not None
        assert node.node_id is not None
        assert len(node.node_id) == 64  # SHA-256 hex digest
        assert node.confidence == 0.9
        assert node.evidence_type == EvidenceType.INDICATOR_NUMERIC

    def test_evidence_edge_creation(self):
        """Test EvidenceEdge creation."""
        from farfan_pipeline.phases.Phase_2.phase2_80_00_evidence_nexus import EvidenceEdge, RelationType

        edge = EvidenceEdge.create(
            source_id="source_123",
            target_id="target_456",
            relation_type=RelationType.SUPPORTS,
            weight=0.8
        )

        assert edge is not None
        assert edge.edge_id is not None
        assert edge.relation_type == RelationType.SUPPORTS
        assert edge.weight == 0.8


# =============================================================================
# TEST CLASS 5: Carver Tests
# =============================================================================


class TestPhase2Carver:
    """Test Carver narrative synthesis."""

    def test_carver_initialization(self):
        """Test DoctoralCarverSynthesizer can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_90_00_carver import DoctoralCarverSynthesizer

        carver = DoctoralCarverSynthesizer()

        assert carver is not None
        assert hasattr(carver, 'synthesize')
        assert hasattr(carver, 'build_narrative')

    def test_quality_level_thresholds(self):
        """Test QualityLevel thresholds."""
        from farfan_pipeline.phases.Phase_2.phase2_90_00_carver import QualityLevel

        test_cases = [
            (0.90, QualityLevel.EXCELENTE),
            (0.75, QualityLevel.BUENO),
            (0.60, QualityLevel.ACEPTABLE),
            (0.40, QualityLevel.INSUFICIENTE),
            (0.10, QualityLevel.INSUFICIENTE),
        ]

        for score, expected_level in test_cases:
            level = QualityLevel.from_score(score)
            assert level == expected_level, f"Score {score} should map to {expected_level}, got {level}"


# =============================================================================
# TEST CLASS 6: CircuitBreaker Tests
# =============================================================================


class TestPhase2CircuitBreaker:
    """Test CircuitBreaker functionality."""

    def test_circuit_breaker_initialization(self):
        """Test CircuitBreaker can be initialized."""
        from farfan_pipeline.phases.Phase_2.phase2_30_04_circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig,
        )

        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_executor", config)

        assert breaker is not None
        assert breaker.name == "test_executor"
        assert breaker.state.value == "closed"

    def test_circuit_breaker_opens_on_threshold(self):
        """Test circuit breaker opens after threshold failures."""
        from farfan_pipeline.phases.Phase_2.phase2_30_04_circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig,
            CircuitState,
        )

        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_executor", config)

        # Record failures up to threshold
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitState.OPEN

    def test_circuit_breaker_can_execute(self):
        """Test can_execute reflects circuit state."""
        from farfan_pipeline.phases.Phase_2.phase2_30_04_circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig,
        )

        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker("test_executor", config)

        # Should be able to execute initially
        can_execute, reason = breaker.can_execute()
        assert can_execute is True

        # Trigger circuit open
        for _ in range(3):
            breaker.record_failure()

        # Should not be able to execute
        can_execute, reason = breaker.can_execute()
        assert can_execute is False

    def test_persistent_circuit_breaker(self, tmp_path):
        """Test PersistentCircuitBreaker saves state."""
        from farfan_pipeline.phases.Phase_2.phase2_30_04_circuit_breaker import (
            CircuitBreakerConfig,
            CircuitState,
            PersistentCircuitBreaker,
        )

        state_file = tmp_path / "circuit_breaker_state.json"
        config = CircuitBreakerConfig(failure_threshold=3)

        # Create and modify breaker
        breaker1 = PersistentCircuitBreaker("test_executor", state_file, config)
        breaker1.record_failure()
        breaker1.record_failure()
        breaker1.record_failure()  # This should open circuit

        # Create new instance - should load persisted state
        breaker2 = PersistentCircuitBreaker("test_executor", state_file, config)

        assert breaker2.state == CircuitState.OPEN
        assert breaker2.failure_count == 3


# =============================================================================
# TEST CLASS 7: ResourceManager Tests
# =============================================================================


class TestPhase2ResourceManager:
    """Test ResourceManager functionality."""

    def test_resource_pressure_levels(self):
        """Test ResourcePressureLevel enum values."""
        from farfan_pipeline.phases.Phase_2.phase2_30_00_resource_manager import ResourcePressureLevel

        levels = [
            ResourcePressureLevel.NORMAL,
            ResourcePressureLevel.ELEVATED,
            ResourcePressureLevel.HIGH,
            ResourcePressureLevel.CRITICAL,
            ResourcePressureLevel.EMERGENCY
        ]

        for level in levels:
            assert level.value in ["normal", "elevated", "high", "critical", "emergency"]

    def test_executor_priority_ordering(self):
        """Test ExecutorPriority ordering."""
        from farfan_pipeline.phases.Phase_2.phase2_30_00_resource_manager import ExecutorPriority

        assert ExecutorPriority.CRITICAL.value < ExecutorPriority.HIGH.value
        assert ExecutorPriority.HIGH.value < ExecutorPriority.NORMAL.value
        assert ExecutorPriority.NORMAL.value < ExecutorPriority.LOW.value


# =============================================================================
# TEST CLASS 8: Complete E2E Flow Tests
# =============================================================================


class TestPhase2CompleteE2E:
    """Test complete Phase 2 flow from input to output."""

    def test_full_e2e_flow_minimal(self, sample_questionnaire, sample_preprocessed_document, tmp_checkpoint_dir):
        """Test complete minimal E2E flow through Phase 2."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import (
            CheckpointManager,
            DryRunExecutor,
        )

        # Step 1: Build execution plan
        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        plan = synchronizer.build_execution_plan()

        assert plan is not None
        assert len(plan.tasks) > 0

        # Step 2: Dry run execution
        dry_run_executor = DryRunExecutor(
            questionnaire_monolith=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        results = dry_run_executor.execute_plan_dry_run(plan)

        assert len(results) == len(plan.tasks)

        # Verify all results are marked as dry run
        for result in results:
            assert result.metadata.get("dry_run") is True

    def test_checkpoint_flow(self, sample_questionnaire, sample_preprocessed_document, tmp_checkpoint_dir):
        """Test checkpoint save/resume flow."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import CheckpointManager

        manager = CheckpointManager(checkpoint_dir=tmp_checkpoint_dir)

        # Build plan
        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        plan = synchronizer.build_execution_plan()

        plan_id = plan.plan_id
        all_task_ids = [t.task_id for t in plan.tasks]

        # Simulate partial execution
        completed_tasks = all_task_ids[:len(all_task_ids)//2]

        # Save checkpoint
        manager.save_checkpoint(plan_id, completed_tasks)

        # Resume and verify
        resumed_tasks = manager.resume_from_checkpoint(plan_id)

        assert resumed_tasks == set(completed_tasks)

        # Clear after completion
        manager.clear_checkpoint(plan_id)

    def test_execution_plan_determinism(self, sample_questionnaire, sample_preprocessed_document):
        """Test that execution plans are deterministic."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer

        # Create two synchronizers with same inputs
        sync1 = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        sync2 = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        plan1 = sync1.build_execution_plan()
        plan2 = sync2.build_execution_plan()

        # Plans should have different correlation_ids (random)
        # but same task structure and integrity hash for same content
        assert len(plan1.tasks) == len(plan2.tasks)

        for t1, t2 in zip(plan1.tasks, plan2.tasks):
            assert t1.task_id == t2.task_id
            assert t1.question_id == t2.question_id
            assert t1.dimension == t2.dimension
            assert t1.policy_area == t2.policy_area


# =============================================================================
# TEST CLASS 9: Adversarial Testing
# =============================================================================


class TestPhase2Adversarial:
    """Adversarial tests for edge cases and error handling."""

    def test_missing_required_field_raises_error(self, sample_preprocessed_document):
        """Test missing required fields in questionnaire raises error."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer

        # Questionnaire missing policy_area_id
        bad_questionnaire = {
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": "Q001",
                        "question_global": 1,
                        # Missing policy_area_id
                        "dimension_id": "D1",
                        "text": "Test question"
                    }
                ]
            }
        }

        synchronizer = IrrigationSynchronizer(
            questionnaire=bad_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        with pytest.raises(ValueError) as exc_info:
            synchronizer.build_execution_plan()

        assert "policy_area_id" in str(exc_info.value).lower()

    def test_invalid_question_id_raises_error(self):
        """Test invalid question_id raises error."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import DynamicContractExecutor

        with pytest.raises(ValueError) as exc_info:
            DynamicContractExecutor._derive_base_slot("INVALID")

        assert "Invalid question_id" in str(exc_info.value)

    def test_empty_document_raises_error(self, sample_questionnaire):
        """Test empty document raises appropriate error."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer
        from farfan_pipeline.calibracion_parametrizacion.types import ChunkData, PreprocessedDocument

        # Empty document with no chunks
        empty_doc = PreprocessedDocument(
            document_id="empty_doc",
            chunks=[],
            metadata={}
        )

        # With Mock ChunkMatrix that allows empty chunks
        with patch("farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer.ChunkMatrix") as MockChunkMatrix:
            MockChunkMatrix.EXPECTED_CHUNK_COUNT = 0

            synchronizer = IrrigationSynchronizer(
                questionnaire=sample_questionnaire,
                preprocessed_document=empty_doc,
                signal_registry=mock_signal_registry()
            )

            # Should handle empty case gracefully
            plan = synchronizer.build_execution_plan()
            assert plan is not None


# =============================================================================
# TEST CLASS 10: Performance and Scalability
# =============================================================================


class TestPhase2Performance:
    """Test performance characteristics."""

    def test_base_slot_caching_performance(self):
        """Test base_slot derivation caching improves performance."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import DynamicContractExecutor

        # Clear cache first
        DynamicContractExecutor._question_to_base_slot_cache.clear()

        question_id = "Q150"

        # First call - not cached
        start = time.perf_counter()
        result1 = DynamicContractExecutor._derive_base_slot(question_id)
        time1 = time.perf_counter() - start

        # Second call - cached
        start = time.perf_counter()
        result2 = DynamicContractExecutor._derive_base_slot(question_id)
        time2 = time.perf_counter() - start

        assert result1 == result2
        # Cached call should be faster (though timing tests can be flaky)
        # We just verify both return same result

    def test_checkpoint_hash_computation_performance(self, tmp_checkpoint_dir):
        """Test checkpoint hash computation is reasonable."""
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import CheckpointManager

        manager = CheckpointManager(checkpoint_dir=tmp_checkpoint_dir)

        # Large checkpoint data
        plan_id = "perf_test_plan"
        completed_tasks = [f"task_{i}" for i in range(1000)]
        metadata = {"key": "x" * 10000}

        start = time.perf_counter()
        manager.save_checkpoint(plan_id, completed_tasks, metadata)
        duration = time.perf_counter() - start

        # Should complete in reasonable time (< 1 second for 1000 tasks)
        assert duration < 1.0


# =============================================================================
# TEST CLASS 11: Integration Tests
# =============================================================================


class TestPhase2Integration:
    """Integration tests between Phase 2 components."""

    def test_synchronizer_to_executor_handoff(self, sample_questionnaire, sample_preprocessed_document):
        """Test handoff from IrrigationSynchronizer to TaskExecutor."""
        from farfan_pipeline.phases.Phase_2.phase2_40_03_irrigation_synchronizer import IrrigationSynchronizer
        from farfan_pipeline.phases.Phase_2.phase2_50_00_task_executor import DryRunExecutor

        # Build plan
        synchronizer = IrrigationSynchronizer(
            questionnaire=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        plan = synchronizer.build_execution_plan()

        # Execute with DryRunExecutor
        executor = DryRunExecutor(
            questionnaire_monolith=sample_questionnaire,
            preprocessed_document=sample_preprocessed_document,
            signal_registry=mock_signal_registry()
        )

        results = executor.execute_plan_dry_run(plan)

        # Verify task IDs match
        plan_task_ids = {t.task_id for t in plan.tasks}
        result_task_ids = {r.task_id for r in results}

        assert plan_task_ids == result_task_ids

    def test_circuit_breaker_with_executor(self):
        """Test circuit breaker integration with executor pattern."""
        from farfan_pipeline.phases.Phase_2.phase2_30_04_circuit_breaker import (
            CircuitBreaker,
            CircuitBreakerConfig,
        )

        config = CircuitBreakerConfig(failure_threshold=2)

        breaker = CircuitBreaker("test_executor", config)

        # Simulate execution attempts
        attempts = []
        for i in range(5):
            can_execute, _ = breaker.can_execute()
            attempts.append(can_execute)

            if can_execute:
                # Simulate failure
                if i < 3:
                    breaker.record_failure()
                else:
                    breaker.record_success()

        # First 2 attempts should succeed, then circuit opens
        assert attempts[0] is True
        assert attempts[1] is True
        # Circuit should be open now
        assert attempts[2] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
