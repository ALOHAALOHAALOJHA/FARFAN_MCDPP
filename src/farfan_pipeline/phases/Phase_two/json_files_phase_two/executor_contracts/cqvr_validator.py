"""
CQVR Contract Quality Validation and Remediation System
Implements Tier 1/2/3 validation rubric for executor contracts
"""
import json
from typing import Any


class CQVRValidator:
    """Contract Quality Validation with Rubric-based scoring (CQVR v2.0)"""

    def __init__(self):
        self.tier1_weight = 55
        self.tier2_weight = 30
        self.tier3_weight = 15
        self.total_weight = 100

    def validate_contract(self, contract: dict) -> dict[str, Any]:
        """Run full CQVR validation and return detailed report"""
        scores = {
            'A1_identity_schema': self._verify_identity_schema_coherence(contract),
            'A2_method_assembly': self._verify_method_assembly_alignment(contract),
            'A3_signal_integrity': self._verify_signal_requirements(contract),
            'A4_output_schema': self._verify_output_schema(contract),
            'B1_pattern_coverage': self._verify_pattern_coverage(contract),
            'B2_method_specificity': self._verify_method_specificity(contract),
            'B3_validation_rules': self._verify_validation_rules(contract),
            'C1_documentation': self._verify_documentation_quality(contract),
            'C2_human_template': self._verify_human_template(contract),
            'C3_metadata': self._verify_metadata_completeness(contract)
        }

        tier1_score = (scores['A1_identity_schema'] + scores['A2_method_assembly'] +
                      scores['A3_signal_integrity'] + scores['A4_output_schema'])
        tier2_score = (scores['B1_pattern_coverage'] + scores['B2_method_specificity'] +
                      scores['B3_validation_rules'])
        tier3_score = (scores['C1_documentation'] + scores['C2_human_template'] +
                      scores['C3_metadata'])

        total_score = tier1_score + tier2_score + tier3_score
        percentage = (total_score / self.total_weight) * 100

        triage_decision = self._triage_decision(tier1_score, tier2_score, total_score, scores)

        return {
            'total_score': total_score,
            'percentage': percentage,
            'tier1_score': tier1_score,
            'tier2_score': tier2_score,
            'tier3_score': tier3_score,
            'breakdown': scores,
            'triage_decision': triage_decision,
            'passed': percentage >= 80 and tier1_score >= 45
        }

    def _verify_identity_schema_coherence(self, contract: dict) -> int:
        """A1: Identity-Schema coherence (20 pts)"""
        score = 0
        id_map = {
            'question_id': 5,
            'policy_area_id': 5,
            'dimension_id': 5,
            'question_global': 3,
            'base_slot': 2
        }

        identity = contract.get('identity', {})
        schema_props = contract.get('output_contract', {}).get('schema', {}).get('properties', {})

        for field, points in id_map.items():
            identity_val = identity.get(field)
            schema_const = schema_props.get(field, {}).get('const')
            if identity_val == schema_const:
                score += points

        return score

    def _verify_method_assembly_alignment(self, contract: dict) -> int:
        """A2: Method-Assembly alignment (20 pts)"""
        methods = contract.get('method_binding', {}).get('methods', [])
        provides = {m['provides'] for m in methods}

        sources = set()
        for rule in contract.get('evidence_assembly', {}).get('assembly_rules', []):
            for src in rule.get('sources', []):
                if '*' not in src:
                    sources.add(src)

        orphan_sources = sources - provides
        if orphan_sources:
            orphan_penalty = min(10, len(orphan_sources) * 2.5)
            return max(0, int(20 - orphan_penalty))

        unused_ratio = len(provides - sources) / len(provides) if provides else 0
        usage_score = 5 * (1 - unused_ratio)

        method_count_ok = 3 if contract['method_binding']['method_count'] == len(methods) else 0

        return int(10 + usage_score + method_count_ok + 2)

    def _verify_signal_requirements(self, contract: dict) -> int:
        """A3: Signal requirements integrity (10 pts)"""
        reqs = contract.get('signal_requirements', {})

        if reqs.get('mandatory_signals') and reqs.get('minimum_signal_threshold', 0) <= 0:
            return 0

        score = 5

        valid_aggregations = ['weighted_mean', 'max', 'min', 'product', 'voting']
        if reqs.get('signal_aggregation') in valid_aggregations:
            score += 2

        mandatory = reqs.get('mandatory_signals', [])
        if all(isinstance(s, str) and '_' in s for s in mandatory) if mandatory else True:
            score += 3

        return score

    def _verify_output_schema(self, contract: dict) -> int:
        """A4: Output schema validation (5 pts)"""
        schema = contract.get('output_contract', {}).get('schema', {})
        required = set(schema.get('required', []))
        properties = set(schema.get('properties', {}).keys())

        if required.issubset(properties):
            return 5

        missing = required - properties
        penalty = len(missing)
        return max(0, 5 - penalty)

    def _verify_pattern_coverage(self, contract: dict) -> int:
        """B1: Pattern coverage (10 pts)"""
        patterns = contract.get('question_context', {}).get('patterns', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])

        if not patterns:
            return 5

        weights_valid = all(0 < p.get('confidence_weight', 0) <= 1 for p in patterns)
        weight_score = 3 if weights_valid else 0

        ids = [p.get('id') for p in patterns]
        id_score = 2 if len(ids) == len(set(ids)) and all(id and 'PAT-' in id for id in ids) else 0

        return 5 + weight_score + id_score

    def _verify_method_specificity(self, contract: dict) -> int:
        """B2: Methodological specificity (10 pts)"""
        methods = contract.get('output_contract', {}).get('human_readable_output', {}).get(
            'methodological_depth', {}).get('methods', [])

        if not methods:
            return 5

        generic_phrases = ["Execute", "Process results", "Return structured output"]
        total_steps = 0
        non_generic_steps = 0

        for method in methods[:5]:
            steps = method.get('technical_approach', {}).get('steps', [])
            total_steps += len(steps)
            for s in steps:
                if isinstance(s, dict):
                    desc = s.get('description', '')
                else:
                    desc = str(s)
                if not any(g in desc for g in generic_phrases):
                    non_generic_steps += 1

        if total_steps == 0:
            return 5

        specificity_ratio = non_generic_steps / total_steps
        return int(10 * specificity_ratio)

    def _verify_validation_rules(self, contract: dict) -> int:
        """B3: Validation rules (10 pts)"""
        rules = contract.get('validation_rules', {}).get('rules', [])
        expected = contract.get('question_context', {}).get('expected_elements', [])

        if not rules:
            return 5

        failure_score = 2 if contract.get('error_handling', {}).get('failure_contract', {}).get('emit_code') else 0

        return 5 + 3 + failure_score

    def _verify_documentation_quality(self, contract: dict) -> int:
        """C1: Documentation quality (5 pts)"""
        return 3

    def _verify_human_template(self, contract: dict) -> int:
        """C2: Human-readable template (5 pts)"""
        template = contract.get('output_contract', {}).get('human_readable_output', {}).get('template', {})

        score = 0
        question_id = contract.get('identity', {}).get('question_id', '')
        if question_id in str(template.get('title', '')):
            score += 3

        if '{score}' in str(template) and '{evidence' in str(template):
            score += 2

        return score

    def _verify_metadata_completeness(self, contract: dict) -> int:
        """C3: Metadata completeness (5 pts)"""
        identity = contract.get('identity', {})
        score = 0

        if identity.get('contract_hash') and len(identity['contract_hash']) == 64:
            score += 2
        if identity.get('created_at'):
            score += 1
        if identity.get('validated_against_schema'):
            score += 1
        if identity.get('contract_version') and '.' in identity['contract_version']:
            score += 1

        return score

    def _triage_decision(self, tier1: int, tier2: int, total: int, scores: dict) -> str:
        """Determine triage decision"""
        if tier1 < 35:
            return self._reformulate_decision(scores)
        elif tier1 >= 45 and total >= 70:
            return "PARCHEAR_MINOR"
        elif tier1 >= 35 and total >= 60:
            return "PARCHEAR_MAJOR"
        else:
            return self._analyze_borderline(scores)

    def _reformulate_decision(self, scores: dict) -> str:
        """Analyze when Tier 1 fails"""
        blockers = []

        if scores['A1_identity_schema'] < 15:
            blockers.append("IDENTITY_SCHEMA_MISMATCH")
        if scores['A2_method_assembly'] < 12:
            blockers.append("ASSEMBLY_SOURCES_BROKEN")
        if scores['A3_signal_integrity'] < 5:
            blockers.append("SIGNAL_THRESHOLD_ZERO")
        if scores['A4_output_schema'] < 3:
            blockers.append("SCHEMA_INVALID")

        if len(blockers) >= 2:
            return f"REFORMULAR_COMPLETO: {blockers}"
        elif "ASSEMBLY_SOURCES_BROKEN" in blockers:
            return "REFORMULAR_ASSEMBLY"
        elif "IDENTITY_SCHEMA_MISMATCH" in blockers:
            return "REFORMULAR_SCHEMA"
        else:
            return "PARCHEAR_CRITICO"

    def _analyze_borderline(self, scores: dict) -> str:
        """Analyze borderline cases"""
        if scores['B2_method_specificity'] < 3:
            return "PARCHEAR_DOCS"
        if scores['B1_pattern_coverage'] < 6:
            return "PARCHEAR_PATTERNS"
        return "PARCHEAR_MAJOR"


class ContractRemediation:
    """Apply structural corrections to contracts"""

    def apply_structural_corrections(self, contract: dict) -> dict:
        """Apply all structural corrections"""
        contract = self._fix_identity_schema_coherence(contract)
        contract = self._fix_method_assembly_alignment(contract)
        contract = self._fix_output_schema_required(contract)
        return contract

    def _fix_identity_schema_coherence(self, contract: dict) -> dict:
        """Ensure identity and output_schema const fields match"""
        identity = contract.get('identity', {})
        schema_props = contract.get('output_contract', {}).get('schema', {}).get('properties', {})

        for field in ['question_id', 'policy_area_id', 'dimension_id', 'question_global', 'base_slot']:
            identity_val = identity.get(field)
            if identity_val is not None:
                if field in schema_props:
                    schema_props[field]['const'] = identity_val

        return contract

    def _fix_method_assembly_alignment(self, contract: dict) -> dict:
        """Align assembly sources with method provides"""
        methods = contract.get('method_binding', {}).get('methods', [])
        provides = [m['provides'] for m in methods]

        assembly_rules = contract.get('evidence_assembly', {}).get('assembly_rules', [])
        if assembly_rules:
            assembly_rules[0]['sources'] = provides

        return contract

    def _fix_output_schema_required(self, contract: dict) -> dict:
        """Ensure all required fields are defined in properties"""
        schema = contract.get('output_contract', {}).get('schema', {})
        required = schema.get('required', [])
        properties = schema.get('properties', {})

        for field in required:
            if field not in properties:
                properties[field] = {
                    'type': 'object',
                    'additionalProperties': True
                }

        return contract


def validate_and_triage_contract(contract_path: str) -> tuple[dict, str]:
    """Validate contract and return report + triage decision"""
    with open(contract_path) as f:
        contract = json.load(f)

    validator = CQVRValidator()
    report = validator.validate_contract(contract)

    return report, report['triage_decision']
