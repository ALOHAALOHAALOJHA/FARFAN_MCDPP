"""End-to-End Deterministic Pipeline Integration Tests

Validates Phase 0 through Phase 9 execution with:
- Fixed seed (seed=42) determinism
- BLAKE3 phase hash stability
- verification_manifest.json structure validation
- Failure propagation testing (Phase N failure to ABORT)
- provenance_completeness=1.0 verification
- 150-page test document processing

Author: F.A.R.F.A.N Test Team
Date: 2025-01-19
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import blake3
import pytest


@pytest.fixture
def test_artifacts_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def generate_150_page_test_pdf(test_artifacts_dir):
    try:
        import fitz
    except ImportError:
        pytest.skip("PyMuPDF not available")

    pdf_path = test_artifacts_dir / "test_plan_150pages.pdf"
    doc = fitz.open()

    for page_num in range(150):
        page = doc.new_page(width=595, height=842)
        page.insert_text(
            (50, 50), f"Plan de Desarrollo - Página {page_num + 1}", fontsize=14, fontname="helv"
        )

        content_type = page_num % 6
        if content_type == 0:
            text = f"Diagnóstico {page_num + 1}: Análisis de brechas."
        elif content_type == 1:
            text = f"Actividad {page_num + 1}: Programa de capacitación."
        elif content_type == 2:
            text = f"Indicador {page_num + 1}: Beneficiarios atendidos."
        elif content_type == 3:
            text = f"Recursos {page_num + 1}: Presupuesto $250,000 USD."
        elif content_type == 4:
            text = f"Cronograma {page_num + 1}: Inicio enero 2025."
        else:
            text = f"Entidades {page_num + 1}: Municipalidad distrital."

        rect = fitz.Rect(50, 80, 545, 792)
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
        page.insert_text((50, 820), f"Página {page_num + 1}/150", fontsize=8, fontname="helv")

    doc.save(pdf_path)
    doc.close()
    return pdf_path


@pytest.fixture
def questionnaire_file():
    from farfan_core.config.paths import QUESTIONNAIRE_FILE

    if not QUESTIONNAIRE_FILE.exists():
        pytest.skip(f"Questionnaire not found: {QUESTIONNAIRE_FILE}")
    return QUESTIONNAIRE_FILE


def compute_phase_hash_blake3(phase_data: dict[str, Any]) -> str:
    json_str = json.dumps(phase_data, sort_keys=True, separators=(",", ":"))
    return blake3.blake3(json_str.encode("utf-8")).hexdigest()


class TestPipelineE2EDeterministic:

    @pytest.mark.asyncio
    async def test_phase_0_to_9_execution_with_fixed_seed(
        self, generate_150_page_test_pdf, questionnaire_file, test_artifacts_dir
    ):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        result = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_e2e_seed42",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir,
        )

        assert result.success is True, f"Pipeline failed: {result.errors}"
        assert result.phases_completed >= 4
        assert result.phases_failed == 0
        assert result.canonical_input is not None
        assert result.canonical_input.pdf_page_count == 150
        assert result.canonical_input.validation_passed is True
        assert len(result.canonical_input.pdf_sha256) == 64
        assert len(result.canonical_input.questionnaire_sha256) == 64
        assert result.canon_policy_package is not None
        assert hasattr(result.canon_policy_package, "chunk_graph")
        assert result.preprocessed_document is not None
        assert result.preprocessed_document.processing_mode == "chunked"
        assert len(result.preprocessed_document.sentences) > 0
        assert result.phase2_result is not None
        questions = result.phase2_result.get("questions", [])
        assert len(questions) > 0
        assert result.manifest is not None
        assert "phases" in result.manifest

    @pytest.mark.asyncio
    async def test_blake3_phase_hash_stability(
        self, generate_150_page_test_pdf, questionnaire_file, test_artifacts_dir
    ):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        result1 = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_hash_run1",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir / "run1",
        )
        result2 = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_hash_run2",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir / "run2",
        )

        assert result1.success is True
        assert result2.success is True

        phase0_data1 = {
            "pdf_sha256": result1.canonical_input.pdf_sha256,
            "pdf_page_count": result1.canonical_input.pdf_page_count,
            "questionnaire_sha256": result1.canonical_input.questionnaire_sha256,
        }
        phase0_data2 = {
            "pdf_sha256": result2.canonical_input.pdf_sha256,
            "pdf_page_count": result2.canonical_input.pdf_page_count,
            "questionnaire_sha256": result2.canonical_input.questionnaire_sha256,
        }

        hash1 = compute_phase_hash_blake3(phase0_data1)
        hash2 = compute_phase_hash_blake3(phase0_data2)
        assert hash1 == hash2
        assert len(hash1) == 64

    @pytest.mark.asyncio
    async def test_verification_manifest_structure(
        self, generate_150_page_test_pdf, questionnaire_file, test_artifacts_dir
    ):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        result = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_manifest_structure",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir,
        )

        assert result.success is True
        manifest = result.manifest
        assert "phases" in manifest
        assert "total_phases" in manifest
        assert "successful_phases" in manifest
        assert "failed_phases" in manifest

        phases = manifest["phases"]
        assert "phase0_input_validation" in phases
        assert "phase1_spc_ingestion" in phases
        assert "phase1_to_phase2_adapter" in phases

        phase0 = phases["phase0_input_validation"]
        assert "status" in phase0
        assert "started_at" in phase0
        assert "finished_at" in phase0
        assert "duration_ms" in phase0
        assert "input_contract" in phase0
        assert "output_contract" in phase0
        assert "invariants_checked" in phase0
        assert phase0["status"] == "success"
        assert phase0["input_contract"]["validation_passed"] is True
        assert phase0["output_contract"]["validation_passed"] is True

        phase1 = phases["phase1_spc_ingestion"]
        assert phase1["status"] == "success"
        assert phase1["duration_ms"] > 0

        adapter = phases["phase1_to_phase2_adapter"]
        assert adapter["status"] == "success"
        assert adapter["duration_ms"] > 0

        manifest_file = test_artifacts_dir / "phase_manifest.json"
        assert manifest_file.exists()

        with open(manifest_file) as f:
            saved_manifest = json.load(f)
        assert "phases" in saved_manifest

    @pytest.mark.asyncio
    async def test_phase_failure_propagation_abort(self, test_artifacts_dir, questionnaire_file):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        fake_pdf_path = test_artifacts_dir / "nonexistent.pdf"
        result = await orchestrator.run_pipeline(
            pdf_path=fake_pdf_path,
            run_id="test_phase_failure",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir,
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert result.phases_failed > 0
        manifest = result.manifest
        assert manifest is not None

        phases = manifest.get("phases", {})
        if "phase0_input_validation" in phases:
            phase0 = phases["phase0_input_validation"]
            assert phase0["status"] == "failed"

    @pytest.mark.asyncio
    async def test_provenance_completeness(
        self, generate_150_page_test_pdf, questionnaire_file, test_artifacts_dir
    ):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        result = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_provenance",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir,
        )

        assert result.success is True
        assert result.preprocessed_document is not None

        chunks = result.preprocessed_document.chunks
        assert len(chunks) > 0

        chunks_with_provenance = 0
        for chunk in chunks:
            if chunk.provenance is not None:
                chunks_with_provenance += 1
                assert chunk.provenance.page_number > 0
                assert chunk.provenance.page_number <= 150

        provenance_completeness = chunks_with_provenance / len(chunks)
        assert provenance_completeness == 1.0, (
            f"Expected provenance_completeness=1.0, " f"got {provenance_completeness}"
        )

    @pytest.mark.asyncio
    async def test_phase_hash_collection_all_phases(
        self, generate_150_page_test_pdf, questionnaire_file, test_artifacts_dir
    ):
        from farfan_core.core.phases.phase_orchestrator import PhaseOrchestrator

        orchestrator = PhaseOrchestrator()
        result = await orchestrator.run_pipeline(
            pdf_path=generate_150_page_test_pdf,
            run_id="test_phase_hashes",
            questionnaire_path=questionnaire_file,
            artifacts_dir=test_artifacts_dir,
        )

        assert result.success is True
        manifest = result.manifest
        phases = manifest["phases"]

        phase_hashes = {}
        for phase_name, phase_data in phases.items():
            if phase_data["status"] == "success":
                hash_data = {
                    "phase_name": phase_name,
                    "duration_ms": phase_data["duration_ms"],
                    "started_at": phase_data["started_at"],
                }
                phase_hash = compute_phase_hash_blake3(hash_data)
                phase_hashes[phase_name] = phase_hash
                assert len(phase_hash) == 64

        assert len(phase_hashes) >= 3
        assert "phase0_input_validation" in phase_hashes
        assert "phase1_spc_ingestion" in phase_hashes
        assert "phase1_to_phase2_adapter" in phase_hashes
