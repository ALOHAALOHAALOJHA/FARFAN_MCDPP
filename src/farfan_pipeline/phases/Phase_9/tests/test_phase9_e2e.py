"""End-to-End Tests for Phase 9 Report Assembly and Generation."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
import tempfile
import shutil

from farfan_pipeline.phases.Phase_9.phase9_10_00_report_assembly import (
    ReportAssembler,
    AnalysisReport
)
from farfan_pipeline.phases.Phase_9.phase9_10_00_report_generator import ReportGenerator

# Mock dependencies
class MockQuestionnaireProvider:
    def get_data(self):
        return {
            "version": "1.0.0",
            "blocks": {
                "micro_questions": [
                    {
                        "question_id": "Q001",
                        "question_global": 1,
                        "base_slot": "slot1",
                        "scoring": {"modality": "standard"},
                        "dimension": "D1",
                        "policy_area": "PA1"
                    }
                ]
            }
        }
    
    def get_patterns_by_question(self, question_id):
        return [{"pattern_id": "PAT01"}]

class TestPhase9E2E:
    
    @pytest.fixture
    def output_dir(self):
        dir_path = tempfile.mkdtemp()
        yield Path(dir_path)
        shutil.rmtree(dir_path)

    @pytest.fixture
    def execution_results(self):
        return {
            "questions": {
                "Q001": {
                    "score": 0.8,
                    "evidence": ["Some evidence text"],
                    "recommendation": "Maintain",
                    "human_answer": "Good progress."
                }
            },
            "meso_clusters": {
                "CL01": {
                    "cluster_id": "CL01",
                    "raw_meso_score": 0.8,
                    "adjusted_score": 0.75,
                    "dispersion_penalty": 0.05,
                    "peer_penalty": 0.0,
                    "total_penalty": 0.05,
                    "dispersion_metrics": {"cv": 0.1},
                    "micro_scores": [0.8],
                    "metadata": {}
                }
            },
            "macro_summary": {
                "overall_posterior": 0.75,
                "adjusted_score": 0.7,
                "coverage_penalty": 0.05,
                "dispersion_penalty": 0.0,
                "contradiction_penalty": 0.0,
                "total_penalty": 0.05,
                "contradiction_count": 0,
                "recommendations": [
                    {"type": "RISK", "severity": "LOW", "description": "Monitor"}
                ],
                "metadata": {}
            },
            "micro_results": { # For signal usage summary
                 "Q001": {
                     "policy_area_id": "PA1",
                     "patterns_used": ["PAT01"],
                     "completeness": 1.0,
                     "validation": {"status": "passed"}
                 }
            }
        }

    @pytest.fixture
    def enriched_packs(self):
        mock_pack = MagicMock()
        mock_pack.patterns = ["PAT01", "PAT02"]
        return {"PA1": mock_pack}

    def test_assemble_and_generate_report(self, output_dir, execution_results, enriched_packs):
        """Test full flow: Assembler -> Report Object -> Generator -> Artifacts."""
        
        # Mocking compute_hash to avoid needing hashing utils dep
        # We need to mock the MODULE import, not just the attribute, because the module might not exist
        mock_hash_utils = MagicMock()
        mock_hash_utils.compute_hash.return_value = "a"*64
        
        with patch.dict('sys.modules', {'farfan_pipeline.utils.hash_utils': mock_hash_utils}):
            # Configure evidence registry mock to return a valid hash string
            mock_evidence_registry = MagicMock()
            mock_record = MagicMock()
            mock_record.entry_hash = "b" * 64  # Valid 64-char hex string
            mock_evidence_registry.records = [mock_record]

            # 1. Assemble Report
            assembler = ReportAssembler(
                questionnaire_provider=MockQuestionnaireProvider(),
                evidence_registry=mock_evidence_registry,
            )
            
            report = assembler.assemble_report(
                plan_name="TestPlan",
                execution_results=execution_results,
                enriched_packs=enriched_packs
            )
        
        assert isinstance(report, AnalysisReport)
        assert report.metadata.plan_name == "TestPlan"
        assert len(report.micro_analyses) == 1
        assert report.micro_analyses[0].question_id == "Q001"
        assert report.verify_digest() is True

        # 2. Generate Artifacts
        generator = ReportGenerator(
            output_dir=output_dir,
            plan_name="TestPlan",
            enable_charts=False, # Disable charts to avoid matplotlib dep issues in test env if any
            enable_animations=False
        )
        
        artifacts = generator.generate_all(
            report=report,
            generate_pdf=False, # Skip PDF to avoid weasyprint dep issues if missing
            generate_html=True,
            generate_markdown=True
        )
        
        # 3. Verify Artifacts
        assert "html" in artifacts
        assert "markdown" in artifacts
        assert "manifest" in artifacts
        
        assert artifacts["html"].exists()
        assert artifacts["markdown"].exists()
        assert artifacts["manifest"].exists()
        
        # Check manifest content
        manifest_content = json.loads(artifacts["manifest"].read_text())
        assert manifest_content["plan_name"] == "TestPlan"
        assert manifest_content["report_id"] == report.metadata.report_id
        assert "html" in manifest_content["artifacts"]

    def test_institutional_annex_generation(self):
        """Test generation of institutional annex."""
        from farfan_pipeline.phases.Phase_9.phase9_15_00_institutional_entity_annex import (
            InstitutionalEntityAnnexGenerator
        )
        
        annex_generator = InstitutionalEntityAnnexGenerator(min_mentions_for_profile=1)
        
        # Mock inputs
        all_enriched_packs = {
            "PA1": {
                "extraction_summary": {
                    "INSTITUTIONAL_NETWORK": {
                        "matches": [
                            {
                                "entity_id": "ENT1",
                                "canonical_name": "Entity One",
                                "entity_type": "institution",
                                "level": "NATIONAL",
                                "confidence": 0.9,
                                "relations": []
                            }
                        ]
                    }
                }
            }
        }
        all_scored_results = {"PA1": {"questions": []}}
        all_recommendations = {"PA1": []}
        
        annex = annex_generator.generate_institutional_annex(
            all_enriched_packs, all_scored_results, all_recommendations
        )
        
        assert len(annex.entity_profiles) == 1
        assert annex.entity_profiles[0].entity_id == "ENT1"
        assert annex.entity_profiles[0].total_mentions == 1

