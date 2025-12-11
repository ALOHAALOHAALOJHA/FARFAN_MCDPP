from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from jsonschema import Draft7Validator

from farfan_pipeline.config.paths import PROJECT_ROOT
# NEW: Replace legacy evidence modules with EvidenceNexus and Carver
from canonic_phases.Phase_two.evidence_nexus import EvidenceNexus, process_evidence
from canonic_phases.Phase_two.carver import DoctoralCarverSynthesizer

if TYPE_CHECKING:
    from farfan_pipeline.core.orchestrator.core import MethodExecutor
    from farfan_pipeline.core.types import PreprocessedDocument
else:  # pragma: no cover - runtime avoids import to break cycles
    MethodExecutor = Any
    PreprocessedDocument = Any


class BaseExecutorWithContract(ABC):
    """Contract-driven executor that routes all calls through MethodExecutor.

    Supports both v2 and v3 contract formats:
    - v2: Legacy format with method_inputs, assembly_rules, validation_rules at top level
    - v3: New format with identity, executor_binding, method_binding, question_context,
          evidence_assembly, output_contract, validation_rules, etc.

    Contract version is auto-detected based on file name (.v3.json vs .json) and structure.
    """

    _contract_cache: dict[str, dict[str, Any]] = {}
    _schema_validators: dict[str, Draft7Validator] = {}
    _factory_contracts_verified: bool = False
    _factory_verification_errors: list[str] = []

    def __init__(
        self,
        method_executor: MethodExecutor,
        signal_registry: Any,
        config: Any,
        questionnaire_provider: Any,
        calibration_orchestrator: Any | None = None,
        enriched_packs: dict[str, Any] | None = None,
        validation_orchestrator: Any | None = None,
    ) -> None:
        try:
            from farfan_pipeline.core.orchestrator.core import (
                MethodExecutor as _MethodExecutor,
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            raise RuntimeError(
                "Failed to import MethodExecutor for BaseExecutorWithContract invariants. "
                "Ensure farfan_core.core.orchestrator.core is importable before constructing contract executors."
            ) from exc
        if not isinstance(method_executor, _MethodExecutor):
            raise RuntimeError(
                "A valid MethodExecutor instance is required for contract executors."
            )
        self.method_executor = method_executor
        self.signal_registry = signal_registry
        self.config = config
        self.questionnaire_provider = questionnaire_provider
        self.calibration_orchestrator = calibration_orchestrator
        # JOBFRONT 3: Support for enriched signal packs (intelligence layer)
        self.enriched_packs = enriched_packs or {}
        self._use_enriched_signals = len(self.enriched_packs) > 0
        # VALIDATION ORCHESTRATOR: Comprehensive validation tracking
        self.validation_orchestrator = validation_orchestrator
        self._use_validation_orchestrator = validation_orchestrator is not None

    @classmethod
    @abstractmethod
    def get_base_slot(cls) -> str:
        raise NotImplementedError

    @classmethod
    def verify_all_base_contracts(
        cls, class_registry: dict[str, type[object]] | None = None
    ) -> dict[str, Any]:
        """Verify all 30 base executor contracts at factory initialization time.

        This method loads and validates all contracts for D1-Q1 through D6-Q5, checking:
        - Contract files exist and are valid JSON
        - Required fields are present (method_inputs/method_binding, assembly_rules,
          validation_rules, expected_elements)
        - JSON schema compliance (v2 or v3)
        - All referenced method classes exist in the class registry

        Args:
            class_registry: Optional class registry to verify method class existence.
                          If None, will attempt to import and build one.

        Returns:
            dict with keys:
                - passed: bool indicating if all contracts are valid
                - total_contracts: int count of contracts checked
                - errors: list of error messages for failed contracts
                - warnings: list of warning messages
                - verified_contracts: list of base_slot identifiers that passed

        Raises:
            RuntimeError: If verification fails with strict=True
        """
        if cls._factory_contracts_verified:
            return {
                "passed": len(cls._factory_verification_errors) == 0,
                "total_contracts": 30,
                "errors": cls._factory_verification_errors,
                "warnings": [],
                "verified_contracts": list(cls._contract_cache.keys()),
            }

        base_slots = [
            f"D{d}-Q{q}" for d in range(1, 7) for q in range(1, 6)
        ]

        if class_registry is None:
            try:
                from farfan_pipeline.core.orchestrator.class_registry import (
                    build_class_registry,
                )
                class_registry = build_class_registry()
            except Exception as exc:
                cls._factory_verification_errors.append(
                    f"Failed to build class registry for verification: {exc}"
                )

        errors: list[str] = []
        warnings: list[str] = []
        verified_contracts: list[str] = []

        for base_slot in base_slots:
            try:
                result = cls._verify_single_contract(base_slot, class_registry)
                if result["passed"]:
                    verified_contracts.append(base_slot)
                else:
                    errors.extend(
                        f"[{base_slot}] {err}" for err in result["errors"]
                    )
                warnings.extend(
                    f"[{base_slot}] {warn}" for warn in result.get("warnings", [])
                )
            except Exception as exc:
                errors.append(f"[{base_slot}] Unexpected error during verification: {exc}")

        cls._factory_contracts_verified = True
        cls._factory_verification_errors = errors

        return {
            "passed": len(errors) == 0,
            "total_contracts": len(base_slots),
            "errors": errors,
            "warnings": warnings,
            "verified_contracts": verified_contracts,
        }

    @classmethod
    def _verify_single_contract(
        cls, base_slot: str, class_registry: dict[str, type[object]] | None = None
    ) -> dict[str, Any]:
        """Verify a single contract for completeness and validity.

        Args:
            base_slot: Base slot identifier (e.g., "D1-Q1")
            class_registry: Optional class registry for method class verification

        Returns:
            dict with keys:
                - passed: bool
                - errors: list of error messages
                - warnings: list of warning messages
                - contract_version: detected version (v2/v3)
                - contract_path: path to contract file
        """
        errors: list[str] = []
        warnings: list[str] = []

        dimension = int(base_slot[1])
        question = int(base_slot[4])
        q_number = (dimension - 1) * 5 + question
        q_id = f"Q{q_number:03d}"

        v3_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / f"{base_slot}.v3.json"
        )
        v2_path = PROJECT_ROOT / "config" / "executor_contracts" / f"{base_slot}.json"
        v3_specialized_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / "specialized" / f"{q_id}.v3.json"
        )
        v2_specialized_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / "specialized" / f"{q_id}.json"
        )

        contract_path = None
        if v3_path.exists():
            contract_path = v3_path
            expected_version = "v3"
        elif v2_path.exists():
            contract_path = v2_path
            expected_version = "v2"
        elif v3_specialized_path.exists():
            contract_path = v3_specialized_path
            expected_version = "v3"
        elif v2_specialized_path.exists():
            contract_path = v2_specialized_path
            expected_version = "v2"
        else:
            errors.append(
                f"Contract file not found. Tried: {v3_path}, {v2_path}, {v3_specialized_path}, {v2_specialized_path}"
            )
            return {
                "passed": False,
                "errors": errors,
                "warnings": warnings,
                "contract_version": None,
                "contract_path": None,
            }

        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in contract file: {exc}")
            return {
                "passed": False,
                "errors": errors,
                "warnings": warnings,
                "contract_version": expected_version,
                "contract_path": str(contract_path),
            }
        except Exception as exc:
            errors.append(f"Failed to read contract file: {exc}")
            return {
                "passed": False,
                "errors": errors,
                "warnings": warnings,
                "contract_version": expected_version,
                "contract_path": str(contract_path),
            }

        detected_version = cls._detect_contract_version(contract)
        if detected_version != expected_version:
            warnings.append(
                f"Contract structure is {detected_version} but file naming suggests {expected_version}"
            )

        try:
            validator = cls._get_schema_validator(detected_version)
            schema_errors = sorted(validator.iter_errors(contract), key=lambda e: e.path)
            if schema_errors:
                errors.extend(
                    f"Schema validation error: {err.message} at {'.'.join(str(p) for p in err.path)}"
                    for err in schema_errors[:10]
                )
        except FileNotFoundError as exc:
            warnings.append(f"Schema file not found: {exc}. Skipping schema validation.")
        except Exception as exc:
            warnings.append(f"Schema validation error: {exc}")

        if detected_version == "v3":
            v3_errors = cls._verify_v3_contract_fields(contract, base_slot, class_registry)
            errors.extend(v3_errors)
        else:
            v2_errors = cls._verify_v2_contract_fields(contract, base_slot, class_registry)
            errors.extend(v2_errors)

        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "contract_version": detected_version,
            "contract_path": str(contract_path),
        }

    @classmethod
    def _verify_v2_contract_fields(
        cls,
        contract: dict[str, Any],
        base_slot: str,
        class_registry: dict[str, type[object]] | None = None,
    ) -> list[str]:
        """Verify required fields for v2 contract format.

        Args:
            contract: Parsed contract dict
            base_slot: Base slot identifier
            class_registry: Optional class registry for method verification

        Returns:
            List of error messages (empty if all checks pass)
        """
        errors: list[str] = []

        if "method_inputs" not in contract:
            errors.append("Missing required field: method_inputs")
        elif not isinstance(contract["method_inputs"], list):
            errors.append("method_inputs must be a list")
        else:
            method_inputs = contract["method_inputs"]
            if not method_inputs:
                errors.append("method_inputs is empty")
            else:
                for idx, method_spec in enumerate(method_inputs):
                    if not isinstance(method_spec, dict):
                        errors.append(f"method_inputs[{idx}] is not a dict")
                        continue
                    if "class" not in method_spec:
                        errors.append(f"method_inputs[{idx}] missing 'class' field")
                    if "method" not in method_spec:
                        errors.append(f"method_inputs[{idx}] missing 'method' field")

                    if class_registry is not None and "class" in method_spec:
                        class_name = method_spec["class"]
                        if class_name not in class_registry:
                            errors.append(
                                f"method_inputs[{idx}]: class '{class_name}' not found in class registry"
                            )

        if "assembly_rules" not in contract:
            errors.append("Missing required field: assembly_rules")
        elif not isinstance(contract["assembly_rules"], list):
            errors.append("assembly_rules must be a list")

        if "validation_rules" not in contract:
            errors.append("Missing required field: validation_rules")

        return errors

    @classmethod
    def _verify_v3_contract_fields(
        cls,
        contract: dict[str, Any],
        base_slot: str,
        class_registry: dict[str, type[object]] | None = None,
    ) -> list[str]:
        """Verify required fields for v3 contract format.

        Args:
            contract: Parsed contract dict
            base_slot: Base slot identifier
            class_registry: Optional class registry for method verification

        Returns:
            List of error messages (empty if all checks pass)
        """
        errors: list[str] = []

        if "identity" not in contract:
            errors.append("Missing required field: identity")
        else:
            identity = contract["identity"]
            if "base_slot" not in identity:
                errors.append("identity missing 'base_slot' field")
            elif identity["base_slot"] != base_slot:
                errors.append(
                    f"identity.base_slot mismatch: expected {base_slot}, got {identity['base_slot']}"
                )

        if "method_binding" not in contract:
            errors.append("Missing required field: method_binding")
        else:
            method_binding = contract["method_binding"]
            orchestration_mode = method_binding.get("orchestration_mode", "single_method")

            if orchestration_mode == "multi_method_pipeline":
                if "methods" not in method_binding:
                    errors.append("method_binding missing 'methods' array for multi_method_pipeline mode")
                elif not isinstance(method_binding["methods"], list):
                    errors.append("method_binding.methods must be a list")
                else:
                    methods = method_binding["methods"]
                    if not methods:
                        errors.append("method_binding.methods is empty")
                    else:
                        for idx, method_spec in enumerate(methods):
                            if not isinstance(method_spec, dict):
                                errors.append(f"methods[{idx}] is not a dict")
                                continue
                            if "class_name" not in method_spec:
                                errors.append(f"methods[{idx}] missing 'class_name' field")
                            if "method_name" not in method_spec:
                                errors.append(f"methods[{idx}] missing 'method_name' field")

                            if class_registry is not None and "class_name" in method_spec:
                                class_name = method_spec["class_name"]
                                if class_name not in class_registry:
                                    errors.append(
                                        f"methods[{idx}]: class '{class_name}' not found in class registry"
                                    )
            elif "class_name" not in method_binding and "primary_method" not in method_binding:
                errors.append(
                    "method_binding missing 'class_name' or 'primary_method' for single_method mode"
                )
            else:
                class_name = method_binding.get("class_name")
                if not class_name and "primary_method" in method_binding:
                    class_name = method_binding["primary_method"].get("class_name")

                if class_name and class_registry is not None:
                    if class_name not in class_registry:
                        errors.append(
                            f"method_binding: class '{class_name}' not found in class registry"
                        )

        if "evidence_assembly" not in contract:
            errors.append("Missing required field: evidence_assembly")
        else:
            evidence_assembly = contract["evidence_assembly"]
            if "assembly_rules" not in evidence_assembly:
                errors.append("evidence_assembly missing 'assembly_rules' field")
            elif not isinstance(evidence_assembly["assembly_rules"], list):
                errors.append("evidence_assembly.assembly_rules must be a list")

        if "validation_rules" not in contract:
            errors.append("Missing required field: validation_rules")

        if "question_context" not in contract:
            errors.append("Missing required field: question_context")
        else:
            question_context = contract["question_context"]
            if "expected_elements" not in question_context:
                errors.append("question_context missing 'expected_elements' field")

        if "error_handling" not in contract:
            errors.append("Missing required field: error_handling")

        return errors

    @classmethod
    def _get_schema_validator(cls, version: str = "v2") -> Draft7Validator:
        """Get schema validator for the specified contract version.

        Args:
            version: Contract version ("v2" or "v3")

        Returns:
            Draft7Validator for the specified version
        """
        if version not in cls._schema_validators:
            if version == "v3":
                schema_path = (
                    PROJECT_ROOT
                    / "config"
                    / "schemas"
                    / "executor_contract.v3.schema.json"
                )
            else:
                schema_path = PROJECT_ROOT / "config" / "executor_contract.schema.json"

            if not schema_path.exists():
                raise FileNotFoundError(f"Contract schema not found: {schema_path}")
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            cls._schema_validators[version] = Draft7Validator(schema)
        return cls._schema_validators[version]

    @classmethod
    def _detect_contract_version(cls, contract: dict[str, Any]) -> str:
        """Detect contract version from structure.

        v3 contracts have: identity, executor_binding, method_binding, question_context
        v2 contracts have: method_inputs, assembly_rules at top level

        Returns:
            "v3" or "v2"
        """
        v3_indicators = [
            "identity",
            "executor_binding",
            "method_binding",
            "question_context",
        ]
        if all(key in contract for key in v3_indicators):
            return "v3"
        return "v2"

    @classmethod
    def _load_contract(cls) -> dict[str, Any]:
        base_slot = cls.get_base_slot()
        if base_slot in cls._contract_cache:
            return cls._contract_cache[base_slot]

        dimension = int(base_slot[1])
        question = int(base_slot[4])
        q_number = (dimension - 1) * 5 + question
        q_id = f"Q{q_number:03d}"

        v3_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / f"{base_slot}.v3.json"
        )
        v2_path = PROJECT_ROOT / "config" / "executor_contracts" / f"{base_slot}.json"
        v3_specialized_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / "specialized" / f"{q_id}.v3.json"
        )
        v2_specialized_path = (
            PROJECT_ROOT / "config" / "executor_contracts" / "specialized" / f"{q_id}.json"
        )

        if v3_path.exists():
            contract_path = v3_path
            expected_version = "v3"
        elif v2_path.exists():
            contract_path = v2_path
            expected_version = "v2"
        elif v3_specialized_path.exists():
            contract_path = v3_specialized_path
            expected_version = "v3"
        elif v2_specialized_path.exists():
            contract_path = v2_specialized_path
            expected_version = "v2"
        else:
            raise FileNotFoundError(
                f"Contract not found for {base_slot}. "
                f"Tried: {v3_path}, {v2_path}, {v3_specialized_path}, {v2_specialized_path}"
            )

        contract = json.loads(contract_path.read_text(encoding="utf-8"))

        # Detect actual version from structure
        detected_version = cls._detect_contract_version(contract)
        if detected_version != expected_version:
            import logging

            logging.warning(
                f"Contract {contract_path.name} has structure of {detected_version} "
                f"but file naming suggests {expected_version}"
            )

        # Validate with appropriate schema
        validator = cls._get_schema_validator(detected_version)
        errors = sorted(validator.iter_errors(contract), key=lambda e: e.path)
        if errors:
            messages = "; ".join(err.message for err in errors)
            raise ValueError(
                f"Contract validation failed for {base_slot} ({detected_version}): {messages}"
            )

        # Tag contract with version for later use
        contract["_contract_version"] = detected_version

        contract_version = contract.get("contract_version")
        if contract_version and not str(contract_version).startswith("2"):
            raise ValueError(
                f"Unsupported contract_version {contract_version} for {base_slot}; expected v2.x"
            )

        identity_base_slot = contract.get("identity", {}).get("base_slot")
        if identity_base_slot and identity_base_slot != base_slot:
            raise ValueError(
                f"Contract base_slot mismatch: expected {base_slot}, found {identity_base_slot}"
            )

        cls._contract_cache[base_slot] = contract
        return contract

    def _validate_signal_requirements(
        self,
        signal_pack: Any,
        signal_requirements: dict[str, Any],
        base_slot: str,
    ) -> None:
        """Validate that signal requirements from contract are met.

        Args:
            signal_pack: Signal pack retrieved from registry (may be None)
            signal_requirements: signal_requirements section from contract
            base_slot: Base slot identifier for error messages

        Raises:
            RuntimeError: If mandatory signal requirements are not met
        """
        mandatory_signals = signal_requirements.get("mandatory_signals", [])
        minimum_threshold = signal_requirements.get("minimum_signal_threshold", 0.0)

        # Check if mandatory signals are required but no signal pack available
        if mandatory_signals and signal_pack is None:
            raise RuntimeError(
                f"Contract {base_slot} requires mandatory signals {mandatory_signals}, "
                "but no signal pack was retrieved from registry. "
                "Ensure signal registry is properly configured and policy_area_id is valid."
            )

        # If signal pack exists, validate signal strength
        if signal_pack is not None and minimum_threshold > 0:
            # Check if signal pack has strength attribute
            if hasattr(signal_pack, "strength") or (
                isinstance(signal_pack, dict) and "strength" in signal_pack
            ):
                strength = (
                    signal_pack.strength
                    if hasattr(signal_pack, "strength")
                    else signal_pack["strength"]
                )
                if strength < minimum_threshold:
                    raise RuntimeError(
                        f"Contract {base_slot} requires minimum signal threshold {minimum_threshold}, "
                        f"but signal pack has strength {strength}. "
                        "Signal quality is insufficient for execution."
                    )

    @staticmethod
    def _set_nested_value(
        target_dict: dict[str, Any], key_path: str, value: Any
    ) -> None:
        """Set a value in a nested dict using dot-notation key path.

        Args:
            target_dict: The dictionary to modify
            key_path: Dot-separated path (e.g., "text_mining.critical_links")
            value: The value to set

        Example:
            _set_nested_value(d, "a.b.c", 123) → d["a"]["b"]["c"] = 123
        """
        keys = key_path.split(".")
        current = target_dict

        # Navigate to the parent of the final key, creating dicts as needed
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # Key exists but is not a dict, cannot nest further
                raise ValueError(
                    f"Cannot set nested value at '{key_path}': "
                    f"intermediate key '{key}' exists but is not a dict"
                )
            current = current[key]

        # Set the final key
        current[keys[-1]] = value

    def _check_failure_contract(
        self, evidence: dict[str, Any], error_handling: dict[str, Any]
    ) -> None:
        failure_contract = error_handling.get("failure_contract", {})
        abort_conditions = failure_contract.get("abort_if", [])
        if not abort_conditions:
            return

        emit_code = failure_contract.get("emit_code", "GENERIC_ABORT")

        for condition in abort_conditions:
            # Example condition check. This could be made more sophisticated.
            if condition == "missing_required_element" and evidence.get(
                "validation", {}
            ).get("errors"):
                # This logic assumes errors from the validator imply a missing required element,
                # which is true with our new validator.
                raise ValueError(
                    f"Execution aborted by failure contract due to '{condition}'. Emit code: {emit_code}"
                )
            if condition == "incomplete_text" and not evidence.get("metadata", {}).get(
                "text_complete", True
            ):
                raise ValueError(
                    f"Execution aborted by failure contract due to '{condition}'. Emit code: {emit_code}"
                )

    def execute(
        self,
        document: PreprocessedDocument,
        method_executor: MethodExecutor,
        *,
        question_context: dict[str, Any],
    ) -> dict[str, Any]:
        if method_executor is not self.method_executor:
            raise RuntimeError(
                "Mismatched MethodExecutor instance for contract executor"
            )

        base_slot = self.get_base_slot()
        if question_context.get("base_slot") != base_slot:
            raise ValueError(
                f"Question base_slot {question_context.get('base_slot')} does not match executor {base_slot}"
            )

        contract = self._load_contract()
        contract_version = contract.get("_contract_version", "v2")

        if contract_version == "v3":
            return self._execute_v3(document, question_context, contract)
        else:
            return self._execute_v2(document, question_context, contract)

    def _execute_v2(
        self,
        document: PreprocessedDocument,
        question_context: dict[str, Any],
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute using v2 contract format (legacy)."""
        base_slot = self.get_base_slot()
        question_id = question_context.get("question_id")
        question_global = question_context.get("question_global")
        policy_area_id = question_context.get("policy_area_id")
        identity = question_context.get("identity", {})
        patterns = question_context.get("patterns", [])
        expected_elements = question_context.get("expected_elements", [])

        # JOBFRONT 3: Use enriched signal packs if available
        signal_pack = None
        enriched_pack = None
        applicable_patterns = patterns  # Default to contract patterns
        document_context = {}

        if self._use_enriched_signals and policy_area_id in self.enriched_packs:
            # Use enriched intelligence layer
            enriched_pack = self.enriched_packs[policy_area_id]
            signal_pack = enriched_pack.base_pack  # Maintain compatibility

            # Create document context from available metadata
            from farfan_pipeline.core.orchestrator.signal_intelligence_layer import (
                create_document_context,
            )

            doc_metadata = getattr(document, "metadata", {})
            document_context = create_document_context(
                section=doc_metadata.get("section"),
                chapter=doc_metadata.get("chapter"),
                page=doc_metadata.get("page"),
                policy_area=policy_area_id
            )

            # Get context-filtered patterns (REFACTORING #6: context scoping)
            applicable_patterns = enriched_pack.get_patterns_for_context(document_context)

            # Expand patterns semantically (REFACTORING #2: semantic expansion)
            if applicable_patterns and isinstance(applicable_patterns[0], dict):
                pattern_strings = [p.get('pattern', p) if isinstance(p, dict) else p for p in applicable_patterns]
            else:
                pattern_strings = applicable_patterns

            expanded_patterns = enriched_pack.expand_patterns(pattern_strings)
            applicable_patterns = expanded_patterns

        elif self.signal_registry is not None and hasattr(self.signal_registry, "get") and policy_area_id:
            # Fallback to legacy signal registry
            signal_pack = self.signal_registry.get(policy_area_id)

        common_kwargs: dict[str, Any] = {
            "document": document,
            "base_slot": base_slot,
            "raw_text": getattr(document, "raw_text", None),
            "text": getattr(document, "raw_text", None),
            "question_id": question_id,
            "question_global": question_global,
            "policy_area_id": policy_area_id,
            "dimension_id": identity.get("dimension_id"),
            "cluster_id": identity.get("cluster_id"),
            "signal_pack": signal_pack,
            "enriched_pack": enriched_pack,  # NEW: Pass enriched pack
            "document_context": document_context,  # NEW: Pass document context
            "question_patterns": applicable_patterns,  # Use filtered/expanded patterns
            "expected_elements": expected_elements,
        }

        method_outputs: dict[str, Any] = {}
        method_inputs = contract.get("method_inputs", [])
        indexed = list(enumerate(method_inputs))
        sorted_inputs = sorted(
            indexed, key=lambda pair: (pair[1].get("priority", 2), pair[0])
        )
        
        calibration_results = {}
        
        for _, entry in sorted_inputs:
            class_name = entry["class"]
            method_name = entry["method"]
            provides = entry.get("provides", [])
            extra_args = entry.get("args", {})

            payload = {**common_kwargs, **extra_args}
            
            method_id = f"{class_name}.{method_name}"
            
            if self.calibration_orchestrator:
                try:
                    from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_orchestrator import (
                        MethodBelowThresholdError,
                    )
                    
                    calibration_result = self.calibration_orchestrator.calibrate(
                        method_id=method_id,
                        context=payload,
                        evidence=None
                    )
                    
                    calibration_results[method_id] = calibration_result.to_dict()
                    
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(
                        f"[{base_slot}] Calibration: {method_id} → {calibration_result.final_score:.3f}"
                    )
                    
                except MethodBelowThresholdError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(
                        f"[{base_slot}] Method {method_id} FAILED calibration: "
                        f"score={e.score:.3f}, threshold={e.threshold:.3f}"
                    )
                    raise RuntimeError(
                        f"Method {method_id} failed calibration threshold"
                    ) from e
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[{base_slot}] Calibration error for {method_id}: {e}")

            result = self.method_executor.execute(
                class_name=class_name,
                method_name=method_name,
                **payload,
            )

            if "signal_pack" in payload and payload["signal_pack"] is not None:
                if "_signal_usage" not in method_outputs:
                    method_outputs["_signal_usage"] = []
                method_outputs["_signal_usage"].append(
                    {
                        "method": f"{class_name}.{method_name}",
                        "policy_area": payload["signal_pack"].policy_area,
                        "version": payload["signal_pack"].version,
                    }
                )

            if isinstance(provides, str):
                method_outputs[provides] = result
            else:
                for key in provides:
                    method_outputs[key] = result

        assembly_rules = contract.get("assembly_rules", [])
        
        # NEW: Use EvidenceNexus instead of legacy EvidenceAssembler
        nexus_result = process_evidence(
            method_outputs=method_outputs,
            assembly_rules=assembly_rules,
            validation_rules=contract.get("validation_rules", []),
            question_context={
                "question_id": question_id,
                "question_global": question_global,
                "expected_elements": expected_elements,
                "patterns": applicable_patterns,
            },
            signal_pack=signal_pack,  # SISAS: Enable signal provenance
            contract=contract,
        )
        
        evidence = nexus_result["evidence"]
        trace = nexus_result["trace"]
        validation = nexus_result["validation"]

        # JOBFRONT 3: Extract structured evidence if enriched pack available
        completeness = 1.0
        missing_elements = []
        patterns_used = []

        if enriched_pack is not None and expected_elements:
            # Build signal node for evidence extraction
            signal_node = {
                "id": question_id,
                "expected_elements": expected_elements,
                "patterns": applicable_patterns,
                "validations": contract.get("validation_rules", [])
            }

            # Extract structured evidence (REFACTORING #5: evidence structure)
            evidence_result = enriched_pack.extract_evidence(
                text=getattr(document, "raw_text", ""),
                signal_node=signal_node,
                document_context=document_context
            )

            # Merge structured evidence into result
            for element_type, matches in evidence_result.evidence.items():
                if element_type not in evidence:
                    evidence[element_type] = matches

            completeness = evidence_result.completeness
            missing_elements = evidence_result.missing_required

            # Track patterns used (for confidence calculation)
            if isinstance(applicable_patterns, list):
                patterns_used = [p.get('id', p) if isinstance(p, dict) else p
                               for p in applicable_patterns[:10]]  # Top 10

        # Note: Validation is now handled by EvidenceNexus above
        error_handling = contract.get("error_handling", {})

        # JOBFRONT 3: Add contract validation if enriched pack available
        contract_validation = None
        if enriched_pack is not None:
            # Build signal node for contract validation
            signal_node_for_validation = {
                "id": question_id,
                "failure_contract": error_handling.get("failure_contract", {}),
                "validations": validation_rules,
                "expected_elements": expected_elements
            }

            # Validate with contracts (REFACTORING #4: contract validation)
            from farfan_pipeline.core.orchestrator.signal_contract_validator import (
                validate_result_with_orchestrator,
            )

            contract_validation = validate_result_with_orchestrator(
                result=evidence,
                signal_node=signal_node_for_validation,
                orchestrator=self.validation_orchestrator if self._use_validation_orchestrator else None,
                auto_register=self._use_validation_orchestrator
            )

            # Merge contract validation into standard validation
            if not contract_validation.passed:
                validation["status"] = "failed"
                validation["errors"] = validation.get("errors", [])
                validation["errors"].append({
                    "error_code": contract_validation.error_code,
                    "condition_violated": contract_validation.condition_violated,
                    "remediation": contract_validation.remediation,
                    "failures_detailed": [
                        {
                            "type": f.failure_type,
                            "field": f.field_name,
                            "message": f.message,
                            "severity": f.severity,
                            "remediation": f.remediation
                        }
                        for f in contract_validation.failures_detailed[:5]
                    ]
                })
                validation["contract_failed"] = True
                validation["contract_validation_details"] = {
                    "error_code": contract_validation.error_code,
                    "diagnostics": contract_validation.diagnostics,
                    "total_failures": len(contract_validation.failures_detailed)
                }
        elif self._use_validation_orchestrator:
            # Even without enriched pack, use validation orchestrator with basic validation
            from farfan_pipeline.core.orchestrator.signal_contract_validator import (
                validate_result_with_orchestrator,
            )

            signal_node_for_validation = {
                "id": question_id,
                "failure_contract": error_handling.get("failure_contract", {}),
                "validations": {"rules": validation_rules},
                "expected_elements": expected_elements
            }

            contract_validation = validate_result_with_orchestrator(
                result=evidence,
                signal_node=signal_node_for_validation,
                orchestrator=self.validation_orchestrator,
                auto_register=True
            )
        if error_handling:
            evidence_with_validation = {**evidence, "validation": validation}
            self._check_failure_contract(evidence_with_validation, error_handling)

        human_answer_template = contract.get("human_answer_template", "")
        human_answer = ""
        if human_answer_template:
            try:
                human_answer = human_answer_template.format(**evidence)
            except KeyError as e:
                human_answer = f"Error formatting human answer: Missing key {e}. Template: '{human_answer_template}'"
                import logging

                logging.warning(human_answer)

        result = {
            "base_slot": base_slot,
            "question_id": question_id,
            "question_global": question_global,
            "policy_area_id": policy_area_id,
            "dimension_id": identity.get("dimension_id"),
            "cluster_id": identity.get("cluster_id"),
            "evidence": evidence,
            "validation": validation,
            "trace": trace,
            "human_answer": human_answer,
            # JOBFRONT 3: Add intelligence layer metadata
            "completeness": completeness,
            "missing_elements": missing_elements,
            "patterns_used": patterns_used,
            "enriched_signals_enabled": enriched_pack is not None,
            # VALIDATION ORCHESTRATOR: Add validation tracking metadata
            "contract_validation": {
                "enabled": contract_validation is not None,
                "passed": contract_validation.passed if contract_validation else None,
                "error_code": contract_validation.error_code if contract_validation else None,
                "failure_count": len(contract_validation.failures_detailed) if contract_validation else 0,
                "orchestrator_registered": self._use_validation_orchestrator
            },
            # CALIBRATION: Add calibration metadata
            "calibration_metadata": {
                "enabled": self.calibration_orchestrator is not None,
                "results": calibration_results,
                "summary": {
                    "total_methods": len(calibration_results),
                    "average_score": sum(
                        cr["final_score"] for cr in calibration_results.values()
                    ) / len(calibration_results) if calibration_results else 0.0,
                    "min_score": min(
                        (cr["final_score"] for cr in calibration_results.values()),
                        default=0.0
                    ),
                    "max_score": max(
                        (cr["final_score"] for cr in calibration_results.values()),
                        default=0.0
                    ),
                }
            }
        }

        return result

    def _execute_v3(
        self,
        document: PreprocessedDocument,
        question_context_external: dict[str, Any],
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute using v3 contract format.

        In v3, contract contains all context, so we use contract['question_context']
        instead of question_context_external (which comes from orchestrator).
        """
        # Extract identity from contract
        identity = contract["identity"]
        base_slot = identity["base_slot"]
        question_id = identity["question_id"]
        dimension_id = identity["dimension_id"]
        policy_area_id = identity["policy_area_id"]

        # CALIBRATION ENFORCEMENT: Verify calibration status before execution
        calibration = contract.get("calibration", {})
        calibration_status = calibration.get("status", "placeholder")
        if calibration_status == "placeholder":
            abort_on_placeholder = (
                self.config.get("abort_on_placeholder_calibration", True)
                if hasattr(self.config, "get")
                else True
            )
            if abort_on_placeholder:
                note = calibration.get("note", "No calibration note provided")
                raise RuntimeError(
                    f"Contract {base_slot} has placeholder calibration (status={calibration_status}). "
                    f"Execution aborted per policy. Calibration note: {note}"
                )

        # Extract question context from contract (source of truth for v3)
        question_context = contract["question_context"]
        question_global = question_context_external.get(
            "question_global"
        )  # May come from orchestrator
        patterns = question_context.get("patterns", [])
        expected_elements = question_context.get("expected_elements", [])

        # Signal pack
        signal_pack = None
        if (
            self.signal_registry is not None
            and hasattr(self.signal_registry, "get")
            and policy_area_id
        ):
            signal_pack = self.signal_registry.get(policy_area_id)

        # SIGNAL REQUIREMENTS VALIDATION: Verify signal requirements from contract
        signal_requirements = contract.get("signal_requirements", {})
        if signal_requirements:
            self._validate_signal_requirements(
                signal_pack, signal_requirements, base_slot
            )

        # Extract method binding
        method_binding = contract["method_binding"]
        orchestration_mode = method_binding.get("orchestration_mode", "single_method")

        # Prepare common kwargs
        common_kwargs: dict[str, Any] = {
            "document": document,
            "base_slot": base_slot,
            "raw_text": getattr(document, "raw_text", None),
            "text": getattr(document, "raw_text", None),
            "question_id": question_id,
            "question_global": question_global,
            "policy_area_id": policy_area_id,
            "dimension_id": dimension_id,
            "cluster_id": identity.get("cluster_id"),
            "signal_pack": signal_pack,
            "question_patterns": patterns,
            "expected_elements": expected_elements,
            "question_context": question_context,
        }

        # Execute methods based on orchestration mode
        method_outputs: dict[str, Any] = {}
        signal_usage_list: list[dict[str, Any]] = []
        calibration_results: dict[str, Any] = {}

        if orchestration_mode == "multi_method_pipeline":
            # Multi-method execution: process all methods in priority order
            methods = method_binding.get("methods", [])
            if not methods:
                raise ValueError(
                    f"orchestration_mode is 'multi_method_pipeline' but no methods array found in method_binding for {base_slot}"
                )

            # Sort by priority (lower priority number = execute first)
            sorted_methods = sorted(methods, key=lambda m: m.get("priority", 99))

            for method_spec in sorted_methods:
                class_name = method_spec["class_name"]
                method_name = method_spec["method_name"]
                provides = method_spec.get("provides", f"{class_name}.{method_name}")
                priority = method_spec.get("priority", 99)
                
                method_id = f"{class_name}.{method_name}"
                
                if self.calibration_orchestrator:
                    try:
                        from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_orchestrator import (
                            MethodBelowThresholdError,
                        )
                        
                        calibration_result = self.calibration_orchestrator.calibrate(
                            method_id=method_id,
                            context=common_kwargs,
                            evidence=None
                        )
                        
                        calibration_results[method_id] = calibration_result.to_dict()
                        
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.info(
                            f"[{base_slot}] Calibration: {method_id} → {calibration_result.final_score:.3f}"
                        )
                        
                    except MethodBelowThresholdError as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"[{base_slot}] Method {method_id} FAILED calibration: "
                            f"score={e.score:.3f}, threshold={e.threshold:.3f}"
                        )
                        raise RuntimeError(
                            f"Method {method_id} failed calibration threshold"
                        ) from e
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"[{base_slot}] Calibration error for {method_id}: {e}")

                try:
                    result = self.method_executor.execute(
                        class_name=class_name,
                        method_name=method_name,
                        **common_kwargs,
                    )

                    # Store result using nested key structure (e.g., "text_mining.critical_links")
                    self._set_nested_value(method_outputs, provides, result)

                    # Track signal usage for this method
                    if signal_pack is not None:
                        signal_usage_list.append(
                            {
                                "method": f"{class_name}.{method_name}",
                                "policy_area": signal_pack.policy_area,
                                "version": signal_pack.version,
                                "priority": priority,
                            }
                        )

                except Exception as exc:
                    import logging

                    logging.error(
                        f"Method execution failed in multi-method pipeline: {class_name}.{method_name}",
                        exc_info=True,
                    )
                    # Store error in trace for debugging
                    # Store error in a flat structure under _errors[provides]
                    if "_errors" not in method_outputs or not isinstance(
                        method_outputs["_errors"], dict
                    ):
                        method_outputs["_errors"] = {}
                    method_outputs["_errors"][provides] = {
                        "error": str(exc),
                        "method": f"{class_name}.{method_name}",
                    }
                    # Re-raise if error_handling policy requires it
                    error_handling = contract.get("error_handling", {})
                    on_method_failure = error_handling.get(
                        "on_method_failure", "propagate_with_trace"
                    )
                    if on_method_failure == "raise":
                        raise
                    # Otherwise continue with other methods

        else:
            # Single-method execution (backward compatible, default)
            class_name = method_binding.get("class_name")
            method_name = method_binding.get("method_name")

            if not class_name or not method_name:
                # Try primary_method if direct class_name/method_name not found
                primary_method = method_binding.get("primary_method", {})
                class_name = primary_method.get("class_name") or class_name
                method_name = primary_method.get("method_name") or method_name

            if not class_name or not method_name:
                raise ValueError(
                    f"Invalid method_binding for {base_slot}: missing class_name or method_name"
                )
            
            method_id = f"{class_name}.{method_name}"
            
            if self.calibration_orchestrator:
                try:
                    from src.cross_cutting_infrastrucuture.capaz_calibration_parmetrization.calibration_orchestrator import (
                        MethodBelowThresholdError,
                    )
                    
                    calibration_result = self.calibration_orchestrator.calibrate(
                        method_id=method_id,
                        context=common_kwargs,
                        evidence=None
                    )
                    
                    calibration_results[method_id] = calibration_result.to_dict()
                    
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(
                        f"[{base_slot}] Calibration: {method_id} → {calibration_result.final_score:.3f}"
                    )
                    
                except MethodBelowThresholdError as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(
                        f"[{base_slot}] Method {method_id} FAILED calibration: "
                        f"score={e.score:.3f}, threshold={e.threshold:.3f}"
                    )
                    raise RuntimeError(
                        f"Method {method_id} failed calibration threshold"
                    ) from e
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"[{base_slot}] Calibration error for {method_id}: {e}")

            result = self.method_executor.execute(
                class_name=class_name,
                method_name=method_name,
                **common_kwargs,
            )
            method_outputs["primary_analysis"] = result

            # Track signal usage
            if signal_pack is not None:
                signal_usage_list.append(
                    {
                        "method": f"{class_name}.{method_name}",
                        "policy_area": signal_pack.policy_area,
                        "version": signal_pack.version,
                    }
                )

        # Store signal usage in method_outputs for trace
        if signal_usage_list:
            method_outputs["_signal_usage"] = signal_usage_list

        # NEW: Evidence assembly and validation using EvidenceNexus
        evidence_assembly = contract["evidence_assembly"]
        assembly_rules = evidence_assembly["assembly_rules"]
        validation_rules_section = contract["validation_rules"]
        
        nexus_result = process_evidence(
            method_outputs=method_outputs,
            assembly_rules=assembly_rules,
            validation_rules=validation_rules_section.get("rules", []),
            question_context={
                "question_id": question_id,
                "question_global": question_global,
                "policy_area_id": policy_area_id,
                "dimension_id": dimension_id,
                "expected_elements": expected_elements,
                "patterns": patterns,
            },
            signal_pack=signal_pack,  # SISAS: Enable signal provenance
            contract=contract,
            na_policy=validation_rules_section.get("na_policy", "abort_on_critical"),
        )
        
        evidence = nexus_result["evidence"]
        trace = nexus_result["trace"]
        validation = nexus_result["validation"]
        
        # Get error_handling for subsequent validation orchestrator
        error_handling = contract.get("error_handling", {})
        
        # Reconstruct validation_rules_object for compatibility with ValidationOrchestrator
        validation_rules = validation_rules_section.get("rules", [])
        na_policy = validation_rules_section.get("na_policy", "abort_on_critical")
        validation_rules_object = {"rules": validation_rules, "na_policy": na_policy}

        # CONTRACT VALIDATION with ValidationOrchestrator
        contract_validation = None
        if self._use_validation_orchestrator:
            from farfan_pipeline.core.orchestrator.signal_contract_validator import (
                validate_result_with_orchestrator,
            )

            signal_node_for_validation = {
                "id": question_id,
                "failure_contract": error_handling.get("failure_contract", {}),
                "validations": validation_rules_object,
                "expected_elements": expected_elements
            }

            contract_validation = validate_result_with_orchestrator(
                result=evidence,
                signal_node=signal_node_for_validation,
                orchestrator=self.validation_orchestrator,
                auto_register=True
            )

            # Merge contract validation failures into standard validation
            if not contract_validation.passed:
                validation["contract_validation_failed"] = True
                validation["contract_error_code"] = contract_validation.error_code
                validation["contract_remediation"] = contract_validation.remediation
                validation["contract_failures"] = [
                    {
                        "type": f.failure_type,
                        "field": f.field_name,
                        "message": f.message,
                        "severity": f.severity
                    }
                    for f in contract_validation.failures_detailed[:10]
                ]

        # Handle validation failures based on NA policy
        validation_passed = validation.get("passed", True)
        if not validation_passed:
            if na_policy == "abort_on_critical":
                # Error handling will check failure contract below
                pass  # Let error_handling section handle abort
            elif na_policy == "score_zero":
                # Mark result as failed with score zero
                validation["score"] = 0.0
                validation["quality_level"] = "FAILED_VALIDATION"
                validation["na_policy_applied"] = "score_zero"
            elif na_policy == "propagate":
                # Continue with validation errors in result
                validation["na_policy_applied"] = "propagate"
                validation["validation_failed"] = True

        # Error handling
        error_handling = contract["error_handling"]
        if error_handling:
            evidence_with_validation = {**evidence, "validation": validation}
            self._check_failure_contract(evidence_with_validation, error_handling)

        # Build result
        result_data = {
            "base_slot": base_slot,
            "question_id": question_id,
            "question_global": question_global,
            "policy_area_id": policy_area_id,
            "dimension_id": dimension_id,
            "cluster_id": identity.get("cluster_id"),
            "evidence": evidence,
            "validation": validation,
            "trace": trace,
            # CONTRACT VALIDATION METADATA
            "contract_validation": {
                "enabled": contract_validation is not None,
                "passed": contract_validation.passed if contract_validation else None,
                "error_code": contract_validation.error_code if contract_validation else None,
                "failure_count": len(contract_validation.failures_detailed) if contract_validation else 0,
                "orchestrator_registered": self._use_validation_orchestrator
            },
            # CALIBRATION METADATA
            "calibration_metadata": {
                "enabled": self.calibration_orchestrator is not None,
                "results": calibration_results,
                "summary": {
                    "total_methods": len(calibration_results),
                    "average_score": sum(
                        cr["final_score"] for cr in calibration_results.values()
                    ) / len(calibration_results) if calibration_results else 0.0,
                    "min_score": min(
                        (cr["final_score"] for cr in calibration_results.values()),
                        default=0.0
                    ),
                    "max_score": max(
                        (cr["final_score"] for cr in calibration_results.values()),
                        default=0.0
                    ),
                }
            }
        }

        # NEW: Record evidence provenance in EvidenceNexus internal store (if available in nexus_result)
        if "provenance_record" in nexus_result:
            # Provenance is now handled internally by EvidenceNexus
            result_data["provenance"] = nexus_result["provenance_record"]

        # Validate output against output_contract schema if present
        output_contract = contract.get("output_contract", {})
        if output_contract and "schema" in output_contract:
            self._validate_output_contract(
                result_data, output_contract["schema"], base_slot
            )

        # NEW: Generate doctoral-level narrative using Carver synthesizer
        human_readable_config = output_contract.get("human_readable_output", {})
        if human_readable_config or nexus_result.get("graph"):
            # Use Carver to generate PhD-level narrative from evidence graph
            carver = DoctoralCarverSynthesizer()
            
            # Prepare contract interpretation for Carver
            carver_input = {
                "contract": contract,
                "evidence": evidence,
                "validation": validation,
                "graph": nexus_result.get("graph"),
                "question_context": {
                    "question_id": question_id,
                    "question_global": question_global,
                    "dimension_id": dimension_id,
                    "policy_area_id": policy_area_id,
                },
                "signal_pack": {
                    "policy_area": getattr(signal_pack, "policy_area", policy_area_id) if signal_pack else policy_area_id,
                    "version": getattr(signal_pack, "version", "unknown") if signal_pack else "unknown",
                },
            }
            
            try:
                carver_answer = carver.synthesize(carver_input)
                result_data["human_readable_output"] = carver_answer.get("full_text", "")
                result_data["carver_metrics"] = carver_answer.get("metrics", {})
            except Exception as e:
                # Fallback to basic template if Carver fails
                result_data["human_readable_output"] = self._generate_human_readable_output(
                    evidence, validation, human_readable_config, contract
                )
                result_data["carver_error"] = str(e)

        return result_data

    def _validate_output_contract(
        self, result: dict[str, Any], schema: dict[str, Any], base_slot: str
    ) -> None:
        """Validate result against output_contract schema with detailed error messages.

        Args:
            result: Result data to validate
            schema: JSON Schema from contract
            base_slot: Base slot identifier for error messages

        Raises:
            ValueError: If validation fails with detailed path information
        """
        from jsonschema import ValidationError, validate

        try:
            validate(instance=result, schema=schema)
        except ValidationError as e:
            # Enhanced error message with JSON path
            path = (
                ".".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
            )
            raise ValueError(
                f"Output contract validation failed for {base_slot} at '{path}': {e.message}. "
                f"Schema constraint: {e.schema}"
            ) from e

    def _generate_human_readable_output(
        self,
        evidence: dict[str, Any],
        validation: dict[str, Any],
        config: dict[str, Any],
        contract: dict[str, Any],
    ) -> str:
        """Generate production-grade human-readable output from template.

        Implements full template engine with:
        - Variable substitution with dot-notation: {evidence.elements_found_count}
        - Derived metrics: Automatic calculation of means, counts, percentages
        - List formatting: Convert arrays to markdown/html/plain_text lists
        - Methodological depth rendering: Full epistemological documentation
        - Multi-format support: markdown, html, plain_text with proper formatting

        Args:
            evidence: Evidence dict from executor
            validation: Validation dict
            config: human_readable_output config from contract
            contract: Full contract for methodological_depth access

        Returns:
            Formatted string in specified format
        """
        template_config = config.get("template", {})
        format_type = config.get("format", "markdown")
        methodological_depth_config = config.get("methodological_depth", {})

        # Build context for variable substitution
        context = self._build_template_context(evidence, validation, contract)

        # Render each template section
        sections = []

        # Title
        if "title" in template_config:
            sections.append(
                self._render_template_string(
                    template_config["title"], context, format_type
                )
            )

        # Summary
        if "summary" in template_config:
            sections.append(
                self._render_template_string(
                    template_config["summary"], context, format_type
                )
            )

        # Score section
        if "score_section" in template_config:
            sections.append(
                self._render_template_string(
                    template_config["score_section"], context, format_type
                )
            )

        # Elements section
        if "elements_section" in template_config:
            sections.append(
                self._render_template_string(
                    template_config["elements_section"], context, format_type
                )
            )

        # Details (list of items)
        if "details" in template_config and isinstance(
            template_config["details"], list
        ):
            detail_items = [
                self._render_template_string(item, context, format_type)
                for item in template_config["details"]
            ]
            sections.append(self._format_list(detail_items, format_type))

        # Interpretation
        if "interpretation" in template_config:
            # Add methodological interpretation if available
            context["methodological_interpretation"] = (
                self._render_methodological_depth(
                    methodological_depth_config, evidence, validation, format_type
                )
            )
            sections.append(
                self._render_template_string(
                    template_config["interpretation"], context, format_type
                )
            )

        # Recommendations
        if "recommendations" in template_config:
            sections.append(
                self._render_template_string(
                    template_config["recommendations"], context, format_type
                )
            )

        # Join sections with appropriate separator for format
        separator = (
            "\n\n"
            if format_type == "markdown"
            else "\n\n" if format_type == "plain_text" else "<br><br>"
        )
        return separator.join(filter(None, sections))

    def _build_template_context(
        self,
        evidence: dict[str, Any],
        validation: dict[str, Any],
        contract: dict[str, Any],
    ) -> dict[str, Any]:
        """Build comprehensive context for template variable substitution.

        DOCTORAL-LEVEL IMPLEMENTATION: This method transforms raw evidence into
        a rich context suitable for generating human-readable outputs with full
        epistemological rigor, uncertainty quantification, and methodological transparency.

        Args:
            evidence: Evidence dict (normalized by EvidenceAssembler._normalize_for_phase3)
            validation: Validation dict
            contract: Full contract for accessing question_context metadata

        Returns:
            Context dict with all variables, derived metrics, and doctoral-level analytics
        """
        import statistics
        import re

        # Base context
        context = {
            "evidence": evidence.copy(),
            "validation": validation.copy(),
        }

        # ═══════════════════════════════════════════════════════════════════════
        # PHASE 2→3 NORMALIZED FIELD MAPPING
        # Contracts produce: elements_found, confidence_scores, pattern_matches
        # Code also accepts: elements, confidences, patterns (legacy names)
        # ═══════════════════════════════════════════════════════════════════════

        # Elements: primary evidence units
        elements = (
            evidence.get("elements")
            or evidence.get("elements_found")
            or []
        )
        if isinstance(elements, list):
            context["evidence"]["elements_found_count"] = len(elements)
            context["evidence"]["elements_found_list"] = self._format_evidence_list(elements)
            context["evidence"]["elements"] = elements  # Ensure canonical name exists

        # Confidence scores: extract from normalized structure or legacy
        confidence_scores = (
            evidence.get("confidence_scores")
            or evidence.get("confidences")
            or evidence.get("raw_results", {}).get("confidence_scores")
            or []
        )
        if isinstance(confidence_scores, list) and confidence_scores:
            numeric_scores = [s for s in confidence_scores if isinstance(s, (int, float))]
            if numeric_scores:
                context["evidence"]["confidence_scores"] = {
                    "mean": statistics.mean(numeric_scores),
                    "min": min(numeric_scores),
                    "max": max(numeric_scores),
                    "std": statistics.stdev(numeric_scores) if len(numeric_scores) > 1 else 0.0,
                    "count": len(numeric_scores),
                    # DOCTORAL: Credible interval (assuming normal distribution)
                    "ci_lower": statistics.mean(numeric_scores) - 1.96 * (statistics.stdev(numeric_scores) / len(numeric_scores)**0.5) if len(numeric_scores) > 1 else statistics.mean(numeric_scores),
                    "ci_upper": statistics.mean(numeric_scores) + 1.96 * (statistics.stdev(numeric_scores) / len(numeric_scores)**0.5) if len(numeric_scores) > 1 else statistics.mean(numeric_scores),
                }
        else:
            context["evidence"]["confidence_scores"] = {
                "mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0, "count": 0,
                "ci_lower": 0.0, "ci_upper": 0.0
            }

        # Pattern matches: count and analyze
        pattern_matches = (
            evidence.get("pattern_matches")
            or evidence.get("patterns")
            or evidence.get("raw_results", {}).get("pattern_matches")
            or {}
        )
        if isinstance(pattern_matches, dict):
            context["evidence"]["pattern_matches_count"] = len(pattern_matches)
            context["evidence"]["pattern_matches"] = pattern_matches
        elif isinstance(pattern_matches, list):
            context["evidence"]["pattern_matches_count"] = len(pattern_matches)
            context["evidence"]["pattern_matches"] = {f"pattern_{i}": p for i, p in enumerate(pattern_matches)}
        else:
            context["evidence"]["pattern_matches_count"] = 0
            context["evidence"]["pattern_matches"] = {}

        # ═══════════════════════════════════════════════════════════════════════
        # DOCTORAL-LEVEL DERIVED METRICS
        # Extract domain-specific counts from evidence elements
        # ═══════════════════════════════════════════════════════════════════════

        # Official sources: DANE, DNP, SISPRO, Ministerio, etc.
        official_source_patterns = [
            r'\bDANE\b', r'\bDNP\b', r'\bSISPRO\b', r'\bSIVIGILA\b',
            r'\bMinisterio\b', r'\bFiscalía\b', r'\bMedicina Legal\b',
            r'\bObservatorio\b', r'\bSecretaría\b', r'\bContraloría\b'
        ]
        official_sources_count = 0
        if isinstance(elements, list):
            for elem in elements:
                elem_str = str(elem.get("text", elem) if isinstance(elem, dict) else elem)
                for pattern in official_source_patterns:
                    if re.search(pattern, elem_str, re.IGNORECASE):
                        official_sources_count += 1
                        break
        context["evidence"]["official_sources_count"] = official_sources_count

        # Quantitative indicators: numbers with %, rates, indices
        quantitative_patterns = [
            r'\d+[.,]?\d*\s*%', r'tasa de', r'índice de', r'por cada \d+',
            r'\d+[.,]\d+', r'porcentaje', r'proporción'
        ]
        quantitative_count = 0
        if isinstance(elements, list):
            for elem in elements:
                elem_str = str(elem.get("text", elem) if isinstance(elem, dict) else elem)
                for pattern in quantitative_patterns:
                    if re.search(pattern, elem_str, re.IGNORECASE):
                        quantitative_count += 1
                        break
        context["evidence"]["quantitative_indicators_count"] = quantitative_count

        # Temporal series: year references
        temporal_pattern = r'20\d{2}|año\s+\d{4}|periodo|histórico|serie'
        temporal_count = 0
        years_found = set()
        if isinstance(elements, list):
            for elem in elements:
                elem_str = str(elem.get("text", elem) if isinstance(elem, dict) else elem)
                year_matches = re.findall(r'20\d{2}', elem_str)
                years_found.update(year_matches)
                if re.search(temporal_pattern, elem_str, re.IGNORECASE):
                    temporal_count += 1
        context["evidence"]["temporal_series_count"] = len(years_found)
        context["evidence"]["years_referenced"] = sorted(years_found) if years_found else []

        # Territorial coverage detection
        territorial_patterns = {
            "municipal": r'\bmunicipal\b|\bmunicipio\b',
            "departamental": r'\bdepartamental\b|\bdepartamento\b',
            "nacional": r'\bnacional\b|\bpaís\b',
            "rural": r'\brural\b|\bveredal\b',
            "urbano": r'\burbano\b|\bcabecera\b',
            "PDET": r'\bPDET\b|\bsubregión\b'
        }
        coverages_found = []
        all_elements_text = " ".join(
            str(elem.get("text", elem) if isinstance(elem, dict) else elem)
            for elem in (elements if isinstance(elements, list) else [])
        )
        for coverage_name, pattern in territorial_patterns.items():
            if re.search(pattern, all_elements_text, re.IGNORECASE):
                coverages_found.append(coverage_name)
        context["evidence"]["territorial_coverage"] = (
            ", ".join(coverages_found) if coverages_found else "Not specified"
        )

        # Missing required elements: from validation
        missing_elements = validation.get("errors", [])
        if missing_elements:
            missing_list = [e for e in missing_elements if "missing" in str(e).lower()]
            context["evidence"]["missing_required_elements"] = (
                "; ".join(missing_list[:5]) if missing_list else "None"
            )
        else:
            context["evidence"]["missing_required_elements"] = "None"

        # ═══════════════════════════════════════════════════════════════════════
        # DOCTORAL: STRENGTH OF EVIDENCE ASSESSMENT
        # ═══════════════════════════════════════════════════════════════════════

        # Evidence strength score (0-1) based on multiple factors
        strength_factors = {
            "element_count": min(len(elements) / 10, 1.0) if isinstance(elements, list) else 0.0,
            "source_diversity": min(official_sources_count / 3, 1.0),
            "quantitative_rigor": min(quantitative_count / 5, 1.0),
            "temporal_depth": min(len(years_found) / 3, 1.0),
            "confidence_level": context["evidence"]["confidence_scores"]["mean"],
        }
        evidence_strength = sum(strength_factors.values()) / len(strength_factors)
        context["evidence"]["strength_score"] = round(evidence_strength, 3)
        context["evidence"]["strength_factors"] = strength_factors
        context["evidence"]["strength_level"] = (
            "Strong" if evidence_strength >= 0.7 else
            "Moderate" if evidence_strength >= 0.4 else
            "Weak"
        )

        # ═══════════════════════════════════════════════════════════════════════
        # DOCTORAL: RECOMMENDATIONS ENGINE
        # ═══════════════════════════════════════════════════════════════════════

        recommendations = []

        if official_sources_count < 2:
            recommendations.append(
                "**Data Provenance Gap**: Include additional official sources (DANE, SISPRO, DNP) "
                "to strengthen baseline validity and enable cross-validation."
            )

        if len(years_found) < 2:
            recommendations.append(
                "**Temporal Depth Required**: Incorporate multi-year data series to establish "
                "trends and enable evidence-based target setting."
            )

        if quantitative_count < 3:
            recommendations.append(
                "**Quantitative Rigor Needed**: Add numerical indicators with explicit units "
                "(rates per 100,000, percentages, absolute counts) for measurable baselines."
            )

        if evidence_strength < 0.4:
            recommendations.append(
                "**Evidence Strengthening Priority**: Current evidence base is weak. "
                "Recommend systematic data collection before policy formulation."
            )

        if not coverages_found:
            recommendations.append(
                "**Territorial Specification**: Clarify geographic scope (municipal, rural, urban) "
                "for proper targeting and resource allocation."
            )

        context["evidence"]["recommendations"] = (
            "\n\n".join(recommendations) if recommendations
            else "Evidence base meets minimum quality standards. Consider adding Bayesian uncertainty quantification for enhanced rigor."
        )

        # ═══════════════════════════════════════════════════════════════════════
        # SCORE AND QUALITY LEVEL
        # ═══════════════════════════════════════════════════════════════════════

        context["score"] = validation.get("score", 0.0)
        context["quality_level"] = self._determine_quality_level(
            validation.get("score", 0.0)
        )

        # DOCTORAL: Add epistemic confidence qualifier
        context["epistemic_confidence"] = (
            "High - Multiple independent sources corroborate findings" if official_sources_count >= 3 else
            "Moderate - Limited source triangulation" if official_sources_count >= 1 else
            "Low - Single source or unverified data"
        )

        return context

    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level from score.

        Args:
            score: Numeric score (typically 0.0-3.0)

        Returns:
            Quality level string
        """
        if score >= 2.5:
            return "EXCELLENT"
        elif score >= 2.0:
            return "GOOD"
        elif score >= 1.0:
            return "ACCEPTABLE"
        elif score > 0:
            return "INSUFFICIENT"
        else:
            return "FAILED"

    def _render_template_string(
        self, template: str, context: dict[str, Any], format_type: str
    ) -> str:
        """Render a template string with variable substitution.

        Supports dot-notation: {evidence.elements_found_count}
        Supports arithmetic: {score}/3.0 (rendered as-is, user interprets)

        Args:
            template: Template string with {variable} placeholders
            context: Context dict
            format_type: Output format (markdown, html, plain_text)

        Returns:
            Rendered string with variables substituted
        """
        import re

        def replace_var(match):
            var_path = match.group(1)
            try:
                # Handle dot-notation traversal
                keys = var_path.split(".")
                value = context
                for key in keys:
                    if isinstance(value, dict):
                        value = value[key]
                    else:
                        # Try to get attribute (for objects)
                        value = getattr(value, key, None)
                        if value is None:
                            return f"{{MISSING:{var_path}}}"

                # Format value appropriately
                if isinstance(value, float):
                    return f"{value:.2f}"
                elif isinstance(value, list | dict):
                    return str(value)  # Simple representation
                else:
                    return str(value)
            except (KeyError, AttributeError, TypeError):
                return f"{{MISSING:{var_path}}}"

        # Replace all {variable} patterns
        rendered = re.sub(r"\{([^}]+)\}", replace_var, template)
        return rendered

    def _format_evidence_list(self, elements: list) -> str:
        """Format evidence elements as markdown list.

        Args:
            elements: List of evidence elements

        Returns:
            Markdown-formatted list string
        """
        if not elements:
            return "- No elements found"

        formatted = []
        for elem in elements:
            if isinstance(elem, dict):
                # Try to extract meaningful representation
                elem_str = elem.get("description") or elem.get("type") or str(elem)
            else:
                elem_str = str(elem)
            formatted.append(f"- {elem_str}")

        return "\n".join(formatted)

    def _format_list(self, items: list[str], format_type: str) -> str:
        """Format a list of items according to output format.

        Args:
            items: List of string items
            format_type: Output format

        Returns:
            Formatted list string
        """
        if format_type == "html":
            items_html = "".join(f"<li>{item}</li>" for item in items)
            return f"<ul>{items_html}</ul>"
        else:  # markdown or plain_text
            return "\n".join(f"- {item}" for item in items)

    def _render_methodological_depth(
        self,
        config: dict[str, Any],
        evidence: dict[str, Any],
        validation: dict[str, Any],
        format_type: str,
    ) -> str:
        """Render methodological depth section with epistemological foundations.

        Transforms v3 contract's methodological_depth into comprehensive documentation.

        Args:
            config: methodological_depth config from contract
            evidence: Evidence dict for contextualization
            validation: Validation dict
            format_type: Output format

        Returns:
            Formatted methodological depth documentation
        """
        if not config or "methods" not in config:
            return "Methodological documentation not available for this executor."

        sections = []

        # Header
        if format_type == "markdown":
            sections.append("#### Methodological Foundations\n")
        elif format_type == "html":
            sections.append("<h4>Methodological Foundations</h4>")
        else:
            sections.append("METHODOLOGICAL FOUNDATIONS\n")

        methods = config.get("methods", [])

        for method_info in methods:
            method_name = method_info.get("method_name", "Unknown")
            class_name = method_info.get("class_name", "Unknown")
            priority = method_info.get("priority", 0)
            role = method_info.get("role", "analysis")

            # Method header
            if format_type == "markdown":
                sections.append(
                    f"##### {class_name}.{method_name} (Priority {priority}, Role: {role})\n"
                )
            else:
                sections.append(
                    f"\n{class_name}.{method_name} (Priority {priority}, Role: {role})\n"
                )

            # Epistemological foundation
            epist = method_info.get("epistemological_foundation", {})
            if epist:
                sections.append(
                    self._render_epistemological_foundation(epist, format_type)
                )

            # Technical approach
            technical = method_info.get("technical_approach", {})
            if technical:
                sections.append(self._render_technical_approach(technical, format_type))

            # Output interpretation
            output_interp = method_info.get("output_interpretation", {})
            if output_interp:
                sections.append(
                    self._render_output_interpretation(output_interp, format_type)
                )

        # Method combination logic
        combination = config.get("method_combination_logic", {})
        if combination:
            sections.append(self._render_method_combination(combination, format_type))

        return "\n\n".join(filter(None, sections))

    def _render_epistemological_foundation(
        self, foundation: dict[str, Any], format_type: str
    ) -> str:
        """Render epistemological foundation section.

        Args:
            foundation: Epistemological foundation dict
            format_type: Output format

        Returns:
            Formatted epistemological foundation text
        """
        parts = []

        paradigm = foundation.get("paradigm")
        if paradigm:
            parts.append(f"**Paradigm**: {paradigm}")

        ontology = foundation.get("ontological_basis")
        if ontology:
            parts.append(f"**Ontological Basis**: {ontology}")

        stance = foundation.get("epistemological_stance")
        if stance:
            parts.append(f"**Epistemological Stance**: {stance}")

        framework = foundation.get("theoretical_framework", [])
        if framework:
            parts.append("**Theoretical Framework**:")
            for item in framework:
                parts.append(f"  - {item}")

        justification = foundation.get("justification")
        if justification:
            parts.append(f"**Justification**: {justification}")

        return "\n".join(parts) if format_type != "html" else "<br>".join(parts)

    def _render_technical_approach(
        self, technical: dict[str, Any], format_type: str
    ) -> str:
        """Render technical approach section.

        Args:
            technical: Technical approach dict
            format_type: Output format

        Returns:
            Formatted technical approach text
        """
        parts = []

        method_type = technical.get("method_type")
        if method_type:
            parts.append(f"**Method Type**: {method_type}")

        algorithm = technical.get("algorithm")
        if algorithm:
            parts.append(f"**Algorithm**: {algorithm}")

        steps = technical.get("steps", [])
        if steps:
            parts.append("**Processing Steps**:")
            for step in steps:
                step_num = step.get("step", "?")
                step_name = step.get("name", "Unnamed")
                step_desc = step.get("description", "")
                parts.append(f"  {step_num}. **{step_name}**: {step_desc}")

        assumptions = technical.get("assumptions", [])
        if assumptions:
            parts.append("**Assumptions**:")
            for assumption in assumptions:
                parts.append(f"  - {assumption}")

        limitations = technical.get("limitations", [])
        if limitations:
            parts.append("**Limitations**:")
            for limitation in limitations:
                parts.append(f"  - {limitation}")

        return "\n".join(parts) if format_type != "html" else "<br>".join(parts)

    def _render_output_interpretation(
        self, interpretation: dict[str, Any], format_type: str
    ) -> str:
        """Render output interpretation section.

        Args:
            interpretation: Output interpretation dict
            format_type: Output format

        Returns:
            Formatted output interpretation text
        """
        parts = []

        guide = interpretation.get("interpretation_guide", {})
        if guide:
            parts.append("**Interpretation Guide**:")
            for threshold_name, threshold_desc in guide.items():
                parts.append(f"  - **{threshold_name}**: {threshold_desc}")

        insights = interpretation.get("actionable_insights", [])
        if insights:
            parts.append("**Actionable Insights**:")
            for insight in insights:
                parts.append(f"  - {insight}")

        return "\n".join(parts) if format_type != "html" else "<br>".join(parts)

    def _render_method_combination(
        self, combination: dict[str, Any], format_type: str
    ) -> str:
        """Render method combination logic section.

        Args:
            combination: Method combination dict
            format_type: Output format

        Returns:
            Formatted method combination text
        """
        parts = []

        if format_type == "markdown":
            parts.append("#### Method Combination Strategy\n")
        else:
            parts.append("METHOD COMBINATION STRATEGY\n")

        strategy = combination.get("combination_strategy")
        if strategy:
            parts.append(f"**Strategy**: {strategy}")

        rationale = combination.get("rationale")
        if rationale:
            parts.append(f"**Rationale**: {rationale}")

        fusion = combination.get("evidence_fusion")
        if fusion:
            parts.append(f"**Evidence Fusion**: {fusion}")

        return "\n".join(parts) if format_type != "html" else "<br>".join(parts)
