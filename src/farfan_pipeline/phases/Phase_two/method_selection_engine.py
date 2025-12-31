"""
F.A.R.F.A.N Method Selection Engine
Systematic selection of optimal methods for 300 Executor Contracts

This module implements the PROMPT MAESTRO protocol for selecting methods from
METHODS_DISPENSARY_V4.json for each of the 30 generic questions.
"""

import json
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import itertools


@dataclass
class SemanticProfile:
    """Semantic profile extracted from a question"""
    question_id: str
    question_type: str
    question_text: str
    n1_keywords: List[str]
    n2_operations: List[str]
    n3_veto_conditions: List[str]
    required_capabilities: Set[str]
    complexity_score: float
    domain_weights: Dict[str, float]


@dataclass
class MethodCandidate:
    """A method candidate for selection"""
    method_id: str
    class_name: str
    method_name: str
    level: str
    output_type: str
    fusion_behavior: str
    provides: List[str]
    requires: List[str]
    contract_compatibility: Dict[str, bool]
    was_degraded: bool
    veto_conditions: Optional[Dict] = None
    score: float = 0.0
    rationale: str = ""


class MethodSelectionEngine:
    """Engine for optimal method selection per question"""

    # Domain patterns for semantic analysis
    DOMAIN_PATTERNS = {
        'financial': r'\b(presupuesto|BPIN|PPI|SGP|COP|millones|inversión|recursos|financ|asign)\b',
        'causal': r'\b(causa|efecto|resultado|impacto|teoría de cambio|cadena|vínculo|contribu)\b',
        'logical': r'\b(coherencia|consistencia|contradicción|lógica|factible|articulación|complement)\b',
        'semantic': r'\b(fuente|referencia|identificada|desagregado|territorio|descri)\b',
        'temporal': r'\b(año|período|horizonte|2027|cuatrienio|línea base)\b',
    }

    # TYPE-specific forcing rules
    FORCING_RULES = {
        'TYPE_A': {
            'MUST_INCLUDE_N1': ['extract', 'parse', 'semantic'],
            'MUST_INCLUDE_N2': ['semantic_score', 'dempster'],
            'MUST_INCLUDE_N3': ['contradiction_detection'],
            'FORBIDDEN': ['weighted_mean'],
        },
        'TYPE_B': {
            'MUST_INCLUDE_N1': ['prior', 'likelihood', 'evidence'],
            'MUST_INCLUDE_N2': ['bayesian_update', 'posterior'],
            'MUST_INCLUDE_N3': ['statistical_test', 'p_value', 'sample_size'],
            'FORBIDDEN': [],
        },
        'TYPE_C': {
            'MUST_INCLUDE_N1': ['node', 'edge', 'graph'],
            'MUST_INCLUDE_N2': ['graph_construction', 'dag', 'topological'],
            'MUST_INCLUDE_N3': ['cycle_detection'],
            'FORBIDDEN': ['bidirectional'],
        },
        'TYPE_D': {
            'MUST_INCLUDE_N1': ['financial', 'budget', 'amount'],
            'MUST_INCLUDE_N2': ['financial_aggregation', 'weighted'],
            'MUST_INCLUDE_N3': ['sufficiency_check', 'gap'],
            'FORBIDDEN': ['no_normalization'],
        },
        'TYPE_E': {
            'MUST_INCLUDE_N1': ['fact', 'collation'],
            'MUST_INCLUDE_N2': ['logical_consistency', 'min'],
            'MUST_INCLUDE_N3': ['contradiction_dominance', 'veto'],
            'FORBIDDEN': ['weighted_mean', 'average', 'mean'],
        },
    }

    # Cardinality constraints per level
    CARDINALITY = {
        'N1-EMP': (3, 6),    # (min, max)
        'N2-INF': (2, 4),
        'N3-AUD': (1, 2),
    }

    def __init__(self, classification_path: str, dispensary_path: str):
        """Initialize the selection engine"""
        self.classification_path = Path(classification_path)
        self.dispensary_path = Path(dispensary_path)

        # Load data
        with open(self.classification_path, 'r') as f:
            self.classification_data = json.load(f)

        with open(self.dispensary_path, 'r') as f:
            self.dispensary_data = json.load(f)

        # Build method index
        self.method_index = self._build_method_index()

    def _build_method_index(self) -> Dict[str, List[MethodCandidate]]:
        """Build index of methods by epistemological level"""
        index = {
            'N1-EMP': [],
            'N2-INF': [],
            'N3-AUD': [],
        }

        for class_name, class_data in self.dispensary_data.items():
            if 'methods' not in class_data or not class_data['methods']:
                continue

            for method_name, method_data in class_data['methods'].items():
                if 'epistemological_classification' not in method_data:
                    continue

                epi_class = method_data['epistemological_classification']
                level = epi_class.get('level', '')

                # Only index N1, N2, N3 (skip INFRASTRUCTURE, N4-SYN, PROTOCOL)
                if level not in index:
                    continue

                # Extract method information
                method_id = f"{class_name}.{method_name}"
                output_type = epi_class.get('output_type', 'UNKNOWN')
                fusion_behavior = epi_class.get('fusion_behavior', 'unknown')
                deps = epi_class.get('dependencies', {})
                provides = deps.get('produces', [])
                requires = deps.get('requires', [])
                compat = epi_class.get('contract_compatibility', {})
                veto_cond = epi_class.get('veto_conditions')

                # Check if degraded
                was_degraded = False
                if 'classification_evidence' in epi_class:
                    was_degraded = epi_class['classification_evidence'].get('was_degraded', False)

                candidate = MethodCandidate(
                    method_id=method_id,
                    class_name=class_name,
                    method_name=method_name,
                    level=level,
                    output_type=output_type,
                    fusion_behavior=fusion_behavior,
                    provides=provides,
                    requires=requires,
                    contract_compatibility=compat,
                    was_degraded=was_degraded,
                    veto_conditions=veto_cond,
                )

                index[level].append(candidate)

        return index

    def extract_semantic_profile(self, question_id: str, question_data: Dict) -> SemanticProfile:
        """Extract semantic profile from a question"""
        question_type = question_data['type']
        question_text = question_data['question_text']

        # Extract keywords by pattern matching
        n1_keywords = []
        n2_operations = []
        n3_veto_conditions = []
        domain_weights = {}

        # Analyze text for domain patterns
        for domain, pattern in self.DOMAIN_PATTERNS.items():
            matches = re.findall(pattern, question_text, re.IGNORECASE)
            weight = len(matches) / max(1, len(question_text.split()))
            domain_weights[domain] = min(1.0, weight * 10)  # Normalize

            if matches:
                n1_keywords.extend(matches[:3])  # Top 3 per domain

        # Type-specific keyword extraction
        if question_type == 'TYPE_A':
            n1_keywords.extend(['fuente', 'referencia', 'desagregación'])
            n2_operations.extend(['semantic_bundling', 'dempster_shafer'])
            n3_veto_conditions.append('semantic_contradiction')

        elif question_type == 'TYPE_B':
            n1_keywords.extend(['evidencia', 'datos', 'información'])
            n2_operations.extend(['bayesian_update', 'posterior_calculation'])
            n3_veto_conditions.extend(['p_value > 0.05', 'sample_size < 30'])

        elif question_type == 'TYPE_C':
            n1_keywords.extend(['actividad', 'resultado', 'relación'])
            n2_operations.extend(['graph_construction', 'topological_overlay'])
            n3_veto_conditions.append('cycle_detected')

        elif question_type == 'TYPE_D':
            n1_keywords.extend(['presupuesto', 'recursos', 'asignación'])
            n2_operations.extend(['financial_aggregation', 'weighted_financial_mean'])
            n3_veto_conditions.extend(['budget_gap > 50%', 'budget_gap > 30%'])

        elif question_type == 'TYPE_E':
            n1_keywords.extend(['coherencia', 'factibilidad', 'contradicción'])
            n2_operations.extend(['logical_consistency_check', 'min_consistency'])
            n3_veto_conditions.append('any_contradiction')

        # Calculate complexity score
        complexity_score = (
            len(question_text.split()) / 100.0 +  # Length factor
            sum(domain_weights.values()) / len(domain_weights) +  # Domain coverage
            0.5  # Base complexity
        ) / 2.0

        required_capabilities = set()
        if 'extract' in question_text.lower():
            required_capabilities.add('extraction')
        if 'analiz' in question_text.lower() or 'evalú' in question_text.lower():
            required_capabilities.add('analysis')
        if 'valid' in question_text.lower() or 'verific' in question_text.lower():
            required_capabilities.add('validation')

        return SemanticProfile(
            question_id=question_id,
            question_type=question_type,
            question_text=question_text,
            n1_keywords=list(set(n1_keywords)),
            n2_operations=list(set(n2_operations)),
            n3_veto_conditions=n3_veto_conditions,
            required_capabilities=required_capabilities,
            complexity_score=complexity_score,
            domain_weights=domain_weights,
        )

    def filter_candidates(
        self,
        candidates: List[MethodCandidate],
        question_type: str,
        target_level: str
    ) -> List[MethodCandidate]:
        """Filter candidates by hard constraints"""
        filtered = []

        for candidate in candidates:
            # Hard Constraint 1: Level must match
            if candidate.level != target_level:
                continue

            # Hard Constraint 2: Contract compatibility
            if not candidate.contract_compatibility.get(question_type, False):
                continue

            # Hard Constraint 3: Not degraded
            if candidate.was_degraded:
                continue

            # Hard Constraint 4: Output type must match level
            expected_output = {
                'N1-EMP': 'FACT',
                'N2-INF': 'PARAMETER',
                'N3-AUD': 'CONSTRAINT',
            }
            if candidate.output_type != expected_output.get(target_level):
                continue

            filtered.append(candidate)

        return filtered

    def score_method(
        self,
        method: MethodCandidate,
        profile: SemanticProfile,
        already_selected: List[MethodCandidate]
    ) -> float:
        """Calculate multi-criteria score for a method"""
        score = 0.0

        # O1: Semantic Match (30%)
        method_text = f"{method.method_id} {' '.join(method.provides)}".lower()
        keyword_matches = sum(1 for kw in profile.n1_keywords if kw.lower() in method_text)
        semantic_score = keyword_matches / max(1, len(profile.n1_keywords))
        score += 0.30 * semantic_score

        # O2: Specificity (25%)
        # Methods with more specific names/provides are better
        specificity = min(1.0, len(method.provides) / 3.0)
        score += 0.25 * specificity

        # O3: Complementarity (20%)
        # Diversity of capabilities covered
        selected_provides = set()
        for sel in already_selected:
            selected_provides.update(sel.provides)
        new_provides = set(method.provides) - selected_provides
        complementarity = len(new_provides) / max(1, len(method.provides))
        score += 0.20 * complementarity

        # O4: Efficiency (15%)
        # Prefer methods with fewer dependencies
        efficiency = 1.0 / (1.0 + len(method.requires))
        score += 0.15 * efficiency

        # O5: Traceability (10%)
        # Methods with explicit 'provides' are better
        traceability = 1.0 if method.provides else 0.5
        score += 0.10 * traceability

        return min(1.0, score)

    def check_forcing_rules(
        self,
        selected_methods: Dict[str, List[MethodCandidate]],
        question_type: str
    ) -> Tuple[bool, List[str]]:
        """Check if selection satisfies forcing rules"""
        violations = []
        rules = self.FORCING_RULES.get(question_type, {})

        # Check MUST_INCLUDE rules for each level
        for level in ['N1', 'N2', 'N3']:
            level_key = f'{level}-EMP' if level == 'N1' else f'{level}-INF' if level == 'N2' else f'{level}-AUD'
            must_include = rules.get(f'MUST_INCLUDE_{level}', [])

            if not must_include:
                continue

            level_methods = selected_methods.get(level_key, [])
            level_text = ' '.join([m.method_id.lower() for m in level_methods])

            satisfied = any(pattern.lower() in level_text for pattern in must_include)

            if not satisfied:
                violations.append(
                    f"{question_type} {level}: Missing required pattern from {must_include}"
                )

        # Check FORBIDDEN patterns
        forbidden = rules.get('FORBIDDEN', [])
        for level_key, level_methods in selected_methods.items():
            for method in level_methods:
                method_text = method.method_id.lower()
                for forbidden_pattern in forbidden:
                    if forbidden_pattern.lower() in method_text:
                        violations.append(
                            f"{question_type} {level_key}: Forbidden pattern '{forbidden_pattern}' in {method.method_id}"
                        )

        return len(violations) == 0, violations

    def validate_selection(
        self,
        n1_methods: List[MethodCandidate],
        n2_methods: List[MethodCandidate],
        n3_methods: List[MethodCandidate],
        question_type: str
    ) -> Tuple[bool, List[str]]:
        """Validate coherence of method selection"""
        violations = []

        # 1. Chain of dependencies
        n1_provides = set()
        for m in n1_methods:
            n1_provides.update(m.provides)

        n2_requires = set()
        n2_provides = set()
        for m in n2_methods:
            n2_requires.update(m.requires)
            n2_provides.update(m.provides)

        # Check N2 requirements are satisfied by N1
        unsatisfied_n2 = n2_requires - n1_provides
        if unsatisfied_n2:
            violations.append(f"N2 requires {unsatisfied_n2} not provided by N1")

        # 2. Veto coverage
        has_veto = any(m.veto_conditions is not None for m in n3_methods)
        if not has_veto:
            violations.append("N3 lacks veto conditions (critical failure mode uncovered)")

        # 3. Balance: |N1| > |N2| > |N3|
        if not (len(n1_methods) >= len(n2_methods) >= len(n3_methods)):
            violations.append(
                f"Epistemological imbalance: |N1|={len(n1_methods)}, "
                f"|N2|={len(n2_methods)}, |N3|={len(n3_methods)}"
            )

        # 4. Cardinality constraints
        for level, (min_count, max_count) in self.CARDINALITY.items():
            level_methods = {'N1-EMP': n1_methods, 'N2-INF': n2_methods, 'N3-AUD': n3_methods}[level]
            if not (min_count <= len(level_methods) <= max_count):
                violations.append(
                    f"{level} cardinality violation: "
                    f"expected [{min_count}, {max_count}], got {len(level_methods)}"
                )

        # 5. Type-specific forcing rules
        all_methods = {
            'N1-EMP': n1_methods,
            'N2-INF': n2_methods,
            'N3-AUD': n3_methods,
        }
        forcing_valid, forcing_violations = self.check_forcing_rules(all_methods, question_type)
        violations.extend(forcing_violations)

        return len(violations) == 0, violations

    def select_methods_for_question(self, question_id: str) -> Dict:
        """Execute complete method selection for a question"""
        print(f"\n{'='*80}")
        print(f"Processing {question_id}")
        print(f"{'='*80}")

        # Get question data
        question_data = self.classification_data['contracts'][question_id]
        question_type = question_data['type']

        # Phase 1: Extract semantic profile
        print(f"\n[Phase 1] Extracting semantic profile...")
        profile = self.extract_semantic_profile(question_id, question_data)
        print(f"  Type: {profile.question_type}")
        print(f"  Keywords: {profile.n1_keywords[:5]}")
        print(f"  Complexity: {profile.complexity_score:.2f}")

        # Phase 2-4: Select methods for each level
        selection = {}

        for level in ['N1-EMP', 'N2-INF', 'N3-AUD']:
            print(f"\n[Phase 2-4] Selecting methods for {level}...")

            # Filter candidates
            candidates = self.filter_candidates(
                self.method_index[level],
                question_type,
                level
            )
            print(f"  Filtered to {len(candidates)} candidates (from {len(self.method_index[level])})")

            # Score candidates
            scored_candidates = []
            for candidate in candidates:
                score = self.score_method(candidate, profile, [])
                candidate.score = score
                scored_candidates.append(candidate)

            # Sort by score
            scored_candidates.sort(key=lambda m: m.score, reverse=True)

            # Select top methods within cardinality
            min_count, max_count = self.CARDINALITY[level]
            selected_count = min(max_count, max(min_count, len(scored_candidates)))
            selected = scored_candidates[:selected_count]

            print(f"  Selected {len(selected)} methods (top scores: {[f'{m.score:.2f}' for m in selected[:3]]})")

            selection[level] = {
                'selected_methods': selected,
                'excluded_candidates': scored_candidates[selected_count:selected_count+5]  # Top 5 excluded
            }

        # Phase 5: Validate selection
        print(f"\n[Phase 5] Validating selection...")
        is_valid, violations = self.validate_selection(
            selection['N1-EMP']['selected_methods'],
            selection['N2-INF']['selected_methods'],
            selection['N3-AUD']['selected_methods'],
            question_type
        )

        if is_valid:
            print(f"  ✅ Validation passed")
        else:
            print(f"  ⚠️  Validation warnings: {len(violations)}")
            for v in violations:
                print(f"    - {v}")

        # Build result
        result = {
            'question_id': question_id,
            'question_type': question_type,
            'question_text': profile.question_text,
            'semantic_profile': {
                'n1_keywords': profile.n1_keywords,
                'n2_operations': profile.n2_operations,
                'n3_veto_conditions': profile.n3_veto_conditions,
                'required_capabilities': list(profile.required_capabilities),
                'complexity_score': profile.complexity_score,
                'domain_weights': profile.domain_weights,
            },
            'method_selection': {},
            'validation_results': {
                'dependency_chain_valid': is_valid,
                'violations': violations,
            },
        }

        # Add method selection details
        for level, data in selection.items():
            result['method_selection'][level] = {
                'selected_methods': [
                    {
                        'method_id': m.method_id,
                        'score': m.score,
                        'rationale': f"Match score {m.score:.2f}; provides {m.provides}",
                        'provides': m.provides,
                        'requires': m.requires,
                    }
                    for m in data['selected_methods']
                ],
                'excluded_candidates': [
                    {
                        'method_id': m.method_id,
                        'score': m.score,
                        'exclusion_reason': f"Score {m.score:.2f} below selection threshold"
                    }
                    for m in data['excluded_candidates'][:3]
                ]
            }

        return result

    def process_all_questions(self) -> Dict:
        """Process all 30 questions"""
        results = {
            'metadata': {
                'version': '1.0.0',
                'date': '2025-12-31',
                'protocol': 'PROMPT_MAESTRO_V1',
                'total_questions': 30,
            },
            'selections': {}
        }

        question_ids = [f"Q{i:03d}" for i in range(1, 31)]

        for question_id in question_ids:
            if question_id not in self.classification_data['contracts']:
                print(f"⚠️  {question_id} not found in classification data")
                continue

            try:
                result = self.select_methods_for_question(question_id)
                results['selections'][question_id] = result
            except Exception as e:
                print(f"❌ Error processing {question_id}: {e}")
                import traceback
                traceback.print_exc()

        return results


def main():
    """Main execution"""
    print("=" * 80)
    print("F.A.R.F.A.N METHOD SELECTION ENGINE")
    print("Executing PROMPT MAESTRO Protocol")
    print("=" * 80)

    # Paths
    base_path = Path("/home/user/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL")
    classification_path = base_path / "src/farfan_pipeline/phases/Phase_two/epistemological_assets/PHASE2_CLASSIFICATION_MASTER_ENRICHED.json"
    dispensary_path = base_path / "src/farfan_pipeline/phases/Phase_two/epistemological_assets/METHODS_DISPENSARY_V4.json"
    output_path = base_path / "artifacts/data/methods/method_selection_per_question.json"

    # Initialize engine
    print("\n[Initializing Engine...]")
    engine = MethodSelectionEngine(
        classification_path=str(classification_path),
        dispensary_path=str(dispensary_path),
    )

    print(f"  ✅ Loaded {len(engine.classification_data['contracts'])} questions")
    print(f"  ✅ Indexed {sum(len(v) for v in engine.method_index.values())} methods")
    print(f"    - N1-EMP: {len(engine.method_index['N1-EMP'])} methods")
    print(f"    - N2-INF: {len(engine.method_index['N2-INF'])} methods")
    print(f"    - N3-AUD: {len(engine.method_index['N3-AUD'])} methods")

    # Process all questions
    print("\n[Processing All Questions...]")
    results = engine.process_all_questions()

    # Save results
    print(f"\n[Saving Results...]")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  ✅ Results saved to {output_path}")
    print(f"  ✅ Processed {len(results['selections'])} questions")

    # Summary
    print(f"\n{'='*80}")
    print("EXECUTION SUMMARY")
    print(f"{'='*80}")

    valid_count = sum(
        1 for r in results['selections'].values()
        if r['validation_results']['dependency_chain_valid']
    )

    print(f"  Total questions processed: {len(results['selections'])}")
    print(f"  Valid selections: {valid_count}")
    print(f"  Selections with warnings: {len(results['selections']) - valid_count}")

    print(f"\n✅ Method selection complete!")


if __name__ == "__main__":
    main()
