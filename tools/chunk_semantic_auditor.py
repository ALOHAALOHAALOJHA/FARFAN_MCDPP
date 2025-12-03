#!/usr/bin/env python3
"""
Chunk Semantic Auditor

Offline verification tool for semantic integrity of processed policy chunks.
Ensures chunk content aligns with assigned metadata (policy_area_id, dimension_id).

Usage:
    python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/
    python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/ --threshold 0.65
    python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/ --model-name all-MiniLM-L6-v2

Exit codes:
    0: All chunks pass semantic integrity checks
    1: One or more chunks fail semantic integrity checks
    2: Configuration or runtime error
"""

import argparse
import json
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm


@dataclass
class ChunkMetadata:
    chunk_id: str
    file_path: str
    policy_area_id: str
    dimension_id: str
    text_content: str


@dataclass
class SemanticAuditResult:
    chunk_id: str
    file_path: str
    policy_area_id: str
    dimension_id: str
    coherence_score: float
    passed: bool
    threshold: float


DIMENSION_DESCRIPTIONS = {
    "DIM01": "Inputs dimension: Financial resources, human capital, infrastructure, legal framework, and budgetary allocations required for policy implementation",
    "DIM02": "Activities dimension: Concrete actions, programs, interventions, and operational activities executed to achieve policy objectives",
    "DIM03": "Products dimension: Direct deliverables, tangible outputs, services provided, and immediate results produced by policy activities",
    "DIM04": "Results dimension: Intermediate outcomes, changes in behavior, capacity improvements, and measurable effects on target populations",
    "DIM05": "Impacts dimension: Long-term effects, structural changes, sustainable transformations, and broader societal benefits",
    "DIM06": "Causality dimension: Logical chains, causal relationships, evidence of mechanisms, and explicit theory of change connecting inputs to impacts",
}

POLICY_AREA_DESCRIPTIONS = {
    "PA01": "Policy area 1: Economic development, productive sectors, business competitiveness, innovation, employment generation, and entrepreneurship support",
    "PA02": "Policy area 2: Social welfare, health services, education systems, vulnerable populations, poverty reduction, and social protection programs",
    "PA03": "Policy area 3: Urban planning, infrastructure development, housing policy, public transportation, utilities, and territorial organization",
    "PA04": "Policy area 4: Environmental protection, natural resources, climate change, sustainable development, biodiversity conservation, and ecological resilience",
    "PA05": "Policy area 5: Public security, justice administration, crime prevention, peace building, human rights protection, and conflict resolution",
    "PA06": "Policy area 6: Cultural development, heritage preservation, arts promotion, sports programs, recreation, and cultural identity strengthening",
    "PA07": "Policy area 7: Institutional capacity, public administration, governance quality, transparency, anti-corruption, and democratic strengthening",
    "PA08": "Policy area 8: Rural development, agricultural policy, peasant communities, land tenure, food security, and rural infrastructure",
    "PA09": "Policy area 9: Digital transformation, information technology, connectivity, e-government, digital inclusion, and telecommunications infrastructure",
    "PA10": "Policy area 10: Cross-sectoral integration, inter-institutional coordination, multi-dimensional approaches, and systemic policy coherence",
}


class ChunkSemanticAuditor:
    def __init__(
        self,
        artifacts_dir: Path,
        threshold: float = 0.7,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        verbose: bool = False,
    ) -> None:
        self.artifacts_dir = artifacts_dir
        self.threshold = threshold
        self.model_name = model_name
        self.verbose = verbose
        self.model: SentenceTransformer | None = None
        self.chunks: list[ChunkMetadata] = []
        self.audit_results: list[SemanticAuditResult] = []

    def load_model(self) -> None:
        if self.verbose:
            print(f"Loading sentence transformer model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        if self.verbose:
            print("Model loaded successfully")

    def discover_chunk_artifacts(self) -> list[Path]:
        if not self.artifacts_dir.exists():
            raise FileNotFoundError(
                f"Artifacts directory not found: {self.artifacts_dir}"
            )

        chunk_files = []
        for pattern in ["**/*chunk*.json", "**/*chunks*.json", "**/*segment*.json"]:
            chunk_files.extend(self.artifacts_dir.glob(pattern))

        if self.verbose:
            print(f"Discovered {len(chunk_files)} chunk artifact files")

        return sorted(set(chunk_files))

    def load_chunk_metadata(self, chunk_file: Path) -> list[ChunkMetadata]:
        chunks = []
        try:
            with open(chunk_file, encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                chunk_list = data
            elif isinstance(data, dict) and "chunks" in data:
                chunk_list = data["chunks"]
            else:
                if self.verbose:
                    print(f"Skipping {chunk_file}: unrecognized format")
                return []

            for idx, chunk in enumerate(chunk_list):
                chunk_id = (
                    chunk.get("chunk_id")
                    or chunk.get("id")
                    or f"{chunk_file.stem}_{idx}"
                )
                text_content = chunk.get("text") or chunk.get("content") or ""
                policy_area_id = (
                    chunk.get("policy_area_id") or chunk.get("policy_area") or ""
                )
                dimension_id = chunk.get("dimension_id") or chunk.get("dimension") or ""

                if not text_content or not policy_area_id or not dimension_id:
                    continue

                chunks.append(
                    ChunkMetadata(
                        chunk_id=chunk_id,
                        file_path=str(chunk_file.relative_to(self.artifacts_dir)),
                        policy_area_id=policy_area_id,
                        dimension_id=dimension_id,
                        text_content=text_content,
                    )
                )

        except json.JSONDecodeError:
            if self.verbose:
                print(f"Skipping {chunk_file}: JSON decode error")
        except Exception as e:
            if self.verbose:
                print(f"Error loading {chunk_file}: {e}")

        return chunks

    def load_all_chunks(self) -> None:
        chunk_files = self.discover_chunk_artifacts()
        if not chunk_files:
            print("Warning: No chunk files discovered", file=sys.stderr)
            return

        for chunk_file in tqdm(
            chunk_files, desc="Loading chunks", disable=not self.verbose
        ):
            chunks = self.load_chunk_metadata(chunk_file)
            self.chunks.extend(chunks)

        if self.verbose:
            print(f"Loaded {len(self.chunks)} chunks with complete metadata")

    def compute_semantic_coherence(self, chunk: ChunkMetadata) -> float:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        dimension_desc = DIMENSION_DESCRIPTIONS.get(
            chunk.dimension_id, f"Unknown dimension {chunk.dimension_id}"
        )
        policy_area_desc = POLICY_AREA_DESCRIPTIONS.get(
            chunk.policy_area_id, f"Unknown policy area {chunk.policy_area_id}"
        )

        canonical_description = f"{dimension_desc}. {policy_area_desc}"

        chunk_embedding = self.model.encode(chunk.text_content, convert_to_tensor=True)
        canonical_embedding = self.model.encode(
            canonical_description, convert_to_tensor=True
        )

        similarity = util.cos_sim(chunk_embedding, canonical_embedding).item()

        return float(similarity)

    def audit_chunk(self, chunk: ChunkMetadata) -> SemanticAuditResult:
        coherence_score = self.compute_semantic_coherence(chunk)
        passed = coherence_score >= self.threshold

        return SemanticAuditResult(
            chunk_id=chunk.chunk_id,
            file_path=chunk.file_path,
            policy_area_id=chunk.policy_area_id,
            dimension_id=chunk.dimension_id,
            coherence_score=coherence_score,
            passed=passed,
            threshold=self.threshold,
        )

    def audit_all_chunks(self) -> None:
        if not self.chunks:
            print("No chunks to audit", file=sys.stderr)
            return

        print(f"\nAuditing {len(self.chunks)} chunks with threshold={self.threshold}\n")

        for chunk in tqdm(self.chunks, desc="Auditing chunks"):
            result = self.audit_chunk(chunk)
            self.audit_results.append(result)

    def generate_report(self) -> dict[str, Any]:
        total_chunks = len(self.audit_results)
        failed_chunks = [r for r in self.audit_results if not r.passed]
        passed_chunks = total_chunks - len(failed_chunks)

        if total_chunks == 0:
            avg_score = 0.0
            min_score = 0.0
            max_score = 0.0
        else:
            scores = [r.coherence_score for r in self.audit_results]
            avg_score = float(np.mean(scores))
            min_score = float(np.min(scores))
            max_score = float(np.max(scores))

        report = {
            "metadata": {
                "artifacts_dir": str(self.artifacts_dir),
                "model_name": self.model_name,
                "threshold": self.threshold,
                "total_chunks_audited": total_chunks,
            },
            "summary": {
                "passed": passed_chunks,
                "failed": len(failed_chunks),
                "pass_rate": passed_chunks / total_chunks if total_chunks > 0 else 0.0,
                "average_coherence_score": avg_score,
                "min_coherence_score": min_score,
                "max_coherence_score": max_score,
            },
            "failures": [
                {
                    "chunk_id": r.chunk_id,
                    "file_path": r.file_path,
                    "policy_area_id": r.policy_area_id,
                    "dimension_id": r.dimension_id,
                    "coherence_score": r.coherence_score,
                    "threshold": r.threshold,
                }
                for r in failed_chunks
            ],
        }

        return report

    def save_report(self, report: dict[str, Any], output_file: Path) -> None:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nAudit report saved to: {output_file}")

    def print_summary(self, report: dict[str, Any]) -> None:
        summary = report["summary"]
        metadata = report["metadata"]

        print("\n" + "=" * 80)
        print("CHUNK SEMANTIC AUDIT SUMMARY")
        print("=" * 80)
        print(f"Artifacts Directory: {metadata['artifacts_dir']}")
        print(f"Model: {metadata['model_name']}")
        print(f"Threshold: {metadata['threshold']:.2f}")
        print(f"Total Chunks: {metadata['total_chunks_audited']}")
        print("-" * 80)
        print(f"Passed: {summary['passed']} ({summary['pass_rate']*100:.1f}%)")
        print(f"Failed: {summary['failed']} ({(1-summary['pass_rate'])*100:.1f}%)")
        print(f"Average Score: {summary['average_coherence_score']:.4f}")
        print(f"Min Score: {summary['min_coherence_score']:.4f}")
        print(f"Max Score: {summary['max_coherence_score']:.4f}")
        print("=" * 80)

        if report["failures"]:
            print("\nFAILURES DETECTED:")
            print("-" * 80)
            for failure in report["failures"]:
                print(f"  ⚠️  {failure['chunk_id']}")
                print(f"      File: {failure['file_path']}")
                print(f"      Policy Area: {failure['policy_area_id']}")
                print(f"      Dimension: {failure['dimension_id']}")
                print(
                    f"      Score: {failure['coherence_score']:.4f} (threshold: {failure['threshold']:.2f})"
                )
                print()

    def run(self) -> int:
        try:
            self.load_model()
            self.load_all_chunks()

            if not self.chunks:
                print("ERROR: No valid chunks found to audit", file=sys.stderr)
                return 2

            self.audit_all_chunks()

            report = self.generate_report()

            output_file = self.artifacts_dir / "semantic_audit_report.json"
            self.save_report(report, output_file)
            self.print_summary(report)

            return 0 if report["summary"]["failed"] == 0 else 1

        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            if self.verbose:
                traceback.print_exc()
            return 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit semantic integrity of processed policy chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic audit
  python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/

  # Custom threshold
  python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/ --threshold 0.65

  # Different model
  python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/ --model-name all-mpnet-base-v2

  # Verbose output
  python tools/chunk_semantic_auditor.py --artifacts-dir artifacts/plan1/ --verbose
        """,
    )

    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        required=True,
        help="Path to artifacts directory (e.g., artifacts/plan1/)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Minimum semantic coherence score (default: 0.7)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Sentence transformer model (default: all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    auditor = ChunkSemanticAuditor(
        artifacts_dir=args.artifacts_dir,
        threshold=args.threshold,
        model_name=args.model_name,
        verbose=args.verbose,
    )

    return auditor.run()


if __name__ == "__main__":
    sys.exit(main())
