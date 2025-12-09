# Agent Development Guide (Canonical, Non-Negotiable)

This guide binds all human/automated agents. Purpose: preserve deterministic pipeline, prevent parallel/competing structures, and enforce rigorous hygiene.

---

## 0) Read-First Gate (no refactors/PRs before reading)
Agents MUST read these files in full before proposing or implementing changes:
- `canonic_questionnaire_central/questionnaire_monolith.json`
- `canonic_questionnaire_central/questionnaire_schema.json`
- `canonic_questionnaire_central/pattern_registry.json`
- `sensitive_rules_for_coding/policy_areas_and_dimensions.json`
- `sensitive_rules_for_coding/canonical_notation/notation_metods`
- `sensitive_rules_for_coding/canonical_notation/notation_questions`
- `artifacts/manifests/manifest.json`
- `artifacts/manifests/verification_manifest.json`
- `artifacts/manifests/signal_audit_manifest.json`
- `documentation/design/ORCHESTRATION_ARCHITECTURE.md`
- `documentation/design/ARCHITECTURE.md`
- `documentation/design/OPERATIONAL_GUIDE.md`

No refactor, relocation, or pipeline change may proceed without explicit citations to the relevant sections of these files.

## 1) Canonical Layout (must not drift)
Allowed top-level entries:
- `.github/`, `artifacts/`, `canonic_questionnaire_central/`, `data/`, `documentation/`, `sensitive_rules_for_coding/`, `src/`, `system/`, `requirements.txt`, `pyproject.toml`, `README*`, `install.sh` (if present), `Makefile` (if present).
Everything else at root is forbidden. `.DS_Store` and any filename containing spaces are forbidden.

### Canonical subpaths (must stay here)
- Manifests: `artifacts/manifests/manifest.json`, `signal_audit_manifest.json`, `verification_manifest.json`. No other manifest locations.
- Questionnaire: `canonic_questionnaire_central/questionnaire_monolith.json`, `questionnaire_schema.json`, `pattern_registry.json`, `update_questionnaire_metadata.py`.
- Canonical notation & taxonomy: `sensitive_rules_for_coding/` (all contents).
- Pipeline/orchestration: `src/orchestration/`, `src/canonic_phases/`, `src/cross_cutting_infrastructure/` (renamed from the misspelled path), `src/methods_dispensary/`, `src/batch_concurrence/`, `src/dashboard_atroz_/`, `src/farfan_pipeline/utils/`.
- Data inputs: `data/plans/`.
- Docs: `documentation/design/*.md`.

## 2) Determinism and manifest truthfulness
- `verification_manifest.json` may set `"success": true` only if all 11 phases ran, 300 micro-questions executed, zero failed phases, required artifacts present, hashes recorded, and `PIPELINE_VERIFIED=1` emitted.
- SHA256 for input PDF and outputs must be written; integrity_hmac must never be placeholder.
- If ingestion or dependency errors occur (e.g., Keras 3 vs transformers), the manifest must remain `"success": false`.

## 3) Canonical phases and taxonomy (immutable)
- Phases: exactly 0–10 (11 phases). No new/renumbered phases.
- Dimensions: D1–D6 only. Policy areas: PA01–PA10 only. Clusters per questionnaire JSON only.
- Micro → meso → macro levels must be preserved; no bypass or shortcutting micro.

## 4) Code hygiene
- Type hints everywhere; mypy/pyright strict.
- Line length 100; ruff + black --check enforced.
- Deterministic seeding for all randomness; explicit error handling; no silent failures.
- No new questionnaire control files; no alternative sources of truth.

## 5) Tests and coverage
- Forbidden: weakening/removing assertions to get green. Property-based (hypothesis) failures are real defects.
- Coverage must not regress for touched areas.

## 6) File/folder rules
- No files at root beyond allowlist. No new folders without explicit approval and mapping to existing layers.
- Remove `.DS_Store` and any file with spaces (e.g., rename/delete `financiero_viabilidad_tablas copy.py`).

## 7) Hooks and CI (must be enforced)
- Pre-commit: ruff, black --check, mypy.
- Pre-push: pytest --cov, `scripts/check_layout.py`, manifest/hash verifier.
- CI required checks: lint, format, mypy, pytest+cov, layout guard, manifest/hash verifier. Branch protection on main; CODEOWNERS on canonical paths (orchestration, canonic_phases, cross_cutting_infrastructure, methods_dispensary, questionnaire, sensitive_rules_for_coding, artifacts/manifests, AGENT_DEVELOPMENT.md, .github/workflows).

## 8) Refactors and renames
- The misspelled directory must be corrected to `src/cross_cutting_infrastructure/`; all imports/paths updated in the same change. Do not leave dual copies.
- Dashboard code (`src/dashboard_atroz_/`) is canonical; guard accordingly.

## 9) Behavioral maxims
- Read-first gate is mandatory.
- No shortcuts, no parallel layers, no shadow specs.
- If a change feels like a bypass of these rules, it is a violation.