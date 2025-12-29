from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .audit_log import end_session, hash_data
from .enricher import enrich_inventory
from .rulebook import DEFAULT_RULEBOOK, compute_rulebook_hash
from .validator import validate_enriched


PIPELINE_VERSION = "2.1.0"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(repo_root: Path) -> dict:
    input_path = repo_root / "METHODS_DISPENSARY_SIGNATURES.json"
    output_path = repo_root / "METHODS_DISPENSARY_SIGNATURES_ENRICHED_EPISTEMOLOGY.json"
    audit_path = repo_root / "ENRICHMENT_AUDIT_MANIFEST.json"

    logger.info("Starting enrichment pipeline v%s", PIPELINE_VERSION)
    logger.info("Input: %s", input_path)

    inventory = json.loads(input_path.read_text(encoding="utf-8"))

    # Enriquecer con sesión de auditoría
    enriched, session = enrich_inventory(inventory)

    # Actualizar sesión con metadatos de rulebook
    session.rulebook_hash = compute_rulebook_hash(DEFAULT_RULEBOOK)
    session.pipeline_version = PIPELINE_VERSION

    errors = validate_enriched(enriched)
    enriched["quality_metrics"]["validation_errors"] = errors

    # Derived metrics
    n3_without_veto = 0
    orphan_methods = 0
    for class_name, cls in enriched.items():
        if class_name == "quality_metrics":
            continue
        for method_name, m in (cls.get("methods", {}) or {}).items():
            ec = m.get("epistemological_classification")
            if not ec:
                continue
            if ec.get("level") == "N3-AUD" and ec.get("veto_conditions") is None:
                n3_without_veto += 1
            if ec.get("level") != "INFRASTRUCTURE":
                compat = ec.get("contract_compatibility", {})
                if not any(bool(compat.get(k)) for k in ["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D", "TYPE_E"]):
                    orphan_methods += 1

    enriched["quality_metrics"]["n3_without_veto"] = n3_without_veto
    enriched["quality_metrics"]["orphan_methods"] = orphan_methods

    # Metadatos de trazabilidad
    enriched["_pipeline_metadata"] = {
        "pipeline_version": PIPELINE_VERSION,
        "rulebook_hash": session.rulebook_hash,
        "input_file": str(input_path),
        "input_sha256": sha256_file(input_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Escribir output enriquecido
    output_content = json.dumps(enriched, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    output_path.write_text(output_content, encoding="utf-8")
    output_hash = sha256_file(output_path)

    # Finalizar sesión de auditoría
    final_session = end_session(output_file_hash=output_hash)
    audit_manifest = final_session.to_manifest()

    # Escribir manifest de auditoría
    audit_path.write_text(
        json.dumps(audit_manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    logger.info("Output: %s (%d bytes)", output_path, output_path.stat().st_size)
    logger.info("Audit: %s", audit_path)
    logger.info("Degradations: %d", len(final_session.degradations))
    logger.info("Invariant violations: %d", len(final_session.invariant_violations))

    if final_session.invariant_violations:
        logger.warning("INVARIANT VIOLATIONS DETECTED - REVIEW REQUIRED")
        for v in final_session.invariant_violations[:5]:
            logger.warning("  - [%s] %s", v.get("invariant_id"), v.get("message", "")[:80])

    return {
        "output_file": str(output_path),
        "output_sha256": output_hash,
        "bytes": output_path.stat().st_size,
        "pipeline_version": PIPELINE_VERSION,
        "rulebook_hash": session.rulebook_hash,
        "quality_metrics": enriched["quality_metrics"],
        "audit_manifest": str(audit_path),
        "session_id": final_session.session_id,
        "degradation_count": len(final_session.degradations),
        "invariant_violation_count": len(final_session.invariant_violations),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    manifest = run(repo_root)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
