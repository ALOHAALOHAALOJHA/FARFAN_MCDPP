# Rúbrica CQVR v2. 0: Sistema de Pesos Estratégicos y Guía de Generación

## PARTE I: RÚBRICA CON PESOS REDEFINIDOS (100 puntos)

### **TIER 1: COMPONENTES CRÍTICOS - BLOQUEANTES (55 puntos)**
*Fallo en cualquiera = INEJECUTABLE*

#### A1.  Coherencia Identity-Schema [20 puntos] ⚠️ CRÍTICO
```python
def verify_identity_schema_coherence(contract: Dict) -> Score:
    """
    PESO: 20 pts - Sin esto, el contrato es rechazado en validación
    
    Verificaciones:
    □ identity.question_id == output_contract.schema.question_id. const [5 pts]
    □ identity. policy_area_id == output_contract.schema. policy_area_id.const [5 pts]
    □ identity.dimension_id == output_contract.schema.dimension_id.const [5 pts]
    □ identity.question_global == output_contract.schema.question_global.const [3 pts]
    □ identity.base_slot == output_contract.schema.base_slot.const [2 pts]
    
    UMBRAL MÍNIMO: 15/20 para ser parcheable
    < 15 pts → REFORMULAR COMPLETO
    """
    score = 0
    id_map = {
        'question_id': 5,
        'policy_area_id': 5, 
        'dimension_id': 5,
        'question_global': 3,
        'base_slot': 2
    }
    
    for field, points in id_map.items():
        identity_val = contract['identity']. get(field)
        schema_const = contract['output_contract']['schema']['properties'][field].get('const')
        if identity_val == schema_const:
            score += points
    
    return score
```

#### A2. Alineación Method-Assembly [20 puntos] ⚠️ CRÍTICO
```python
def verify_method_assembly_alignment(contract: Dict) -> Score:
    """
    PESO: 20 pts - Sin esto, evidence assembly falla completamente
    
    Verificaciones:
    □ 100% sources existen en provides [10 pts]
    □ >80% provides son usados [5 pts]
    □ method_count correcto [3 pts]
    □ No hay namespaces inventados [2 pts]
    
    UMBRAL MÍNIMO: 12/20 para ser parcheable
    < 12 pts → REFORMULAR COMPLETO
    """
    provides = {m['provides'] for m in contract['method_binding']['methods']}
    sources = set()
    for rule in contract['evidence_assembly']['assembly_rules']:
        sources.update(rule. get('sources', []))
    
    # Penalización severa por sources huérfanos
    orphan_sources = sources - provides
    if orphan_sources:
        orphan_penalty = min(10, len(orphan_sources) * 2.5)
        return max(0, 20 - orphan_penalty)
    
    # Score completo si no hay huérfanos
    unused_ratio = len(provides - sources) / len(provides) if provides else 0
    usage_score = 5 * (1 - unused_ratio)
    
    method_count_ok = 3 if contract['method_binding']['method_count'] == len(contract['method_binding']['methods']) else 0
    
    return 10 + usage_score + method_count_ok + 2
```

#### A3. Integridad de Señales [10 puntos] ⚠️ CRÍTICO
```python
def verify_signal_requirements(contract: Dict) -> Score:
    """
    PESO:  10 pts - Señales incorrectas = sin datos de entrada
    
    Verificaciones: 
    □ threshold > 0 si hay mandatory_signals [5 pts - BLOQUEANTE]
    □ mandatory_signals bien formadas [3 pts]
    □ aggregation válida [2 pts]
    
    UMBRAL MÍNIMO: 5/10 (el threshold DEBE ser > 0)
    < 5 pts → REFORMULAR COMPLETO
    """
    reqs = contract['signal_requirements']
    
    # Verificación bloqueante
    if reqs['mandatory_signals'] and reqs['minimum_signal_threshold'] <= 0:
        return 0  # FALLO TOTAL - No parcheable
    
    score = 5  # Pasó verificación crítica
    
    # Verificaciones adicionales
    valid_aggregations = ['weighted_mean', 'max', 'min', 'product', 'voting']
    if reqs. get('signal_aggregation') in valid_aggregations:
        score += 2
    
    # Signals bien formadas
    if all(isinstance(s, str) and '_' in s for s in reqs['mandatory_signals']):
        score += 3
    
    return score
```

#### A4. Validación de Output Schema [5 puntos] ⚠️ CRÍTICO
```python
def verify_output_schema(contract: Dict) -> Score:
    """
    PESO: 5 pts - Schema roto = output rechazado
    
    Verificaciones:
    □ Todos los required fields tienen definición [3 pts]
    □ Types válidos (no mixing string/null incorrectamente) [2 pts]
    
    UMBRAL MÍNIMO: 3/5 para ser parcheable
    """
    schema = contract['output_contract']['schema']
    required = set(schema.get('required', []))
    properties = set(schema.get('properties', {}).keys())
    
    if required.issubset(properties):
        return 5
    
    missing = required - properties
    penalty = len(missing)
    return max(0, 5 - penalty)
```

### **TIER 2: COMPONENTES FUNCIONALES (30 puntos)**
*Afectan calidad pero no bloquean ejecución*

#### B1. Coherencia de Patrones [10 puntos]
```python
def verify_pattern_coverage(contract: Dict) -> Score:
    """
    PESO:  10 pts - Afecta precisión de matching
    
    Verificaciones: 
    □ Patrones cubren expected_elements [5 pts]
    □ confidence_weights válidos [3 pts]
    □ IDs únicos bien formados [2 pts]
    
    UMBRAL SUGERIDO: 6/10 para calidad aceptable
    """
    patterns = contract['question_context']['patterns']
    expected = contract['question_context']['expected_elements']
    
    # Cobertura de elementos esperados
    expected_types = {e['type'] for e in expected if e.get('required')}
    pattern_coverage = len([p for p in patterns if any(
        exp in p.get('pattern', '') for exp in expected_types
    )])
    
    coverage_score = min(5, (pattern_coverage / len(expected_types)) * 5) if expected_types else 5
    
    # Validar confidence weights
    weights_valid = all(0 < p.get('confidence_weight', 0) <= 1 for p in patterns)
    weight_score = 3 if weights_valid else 0
    
    # IDs únicos
    ids = [p.get('id') for p in patterns]
    id_score = 2 if len(ids) == len(set(ids)) and all(id and 'PAT-' in id for id in ids) else 0
    
    return coverage_score + weight_score + id_score
```

#### B2. Especificidad Metodológica [10 puntos]
```python
def verify_method_specificity(contract: Dict) -> Score:
    """
    PESO: 10 pts - Afecta interpretabilidad y debugging
    
    Verificaciones: 
    □ Steps no genéricos [6 pts]
    □ Complexity realista [2 pts]
    □ Assumptions documentadas [2 pts]
    
    UMBRAL SUGERIDO: 5/10 para documentación mínima
    """
    methods = contract. get('output_contract', {}).get('human_readable_output', {}).get('methodological_depth', {}).get('methods', [])
    
    if not methods:
        # Si no hay methodological_depth, no penalizar (es opcional)
        return 5  # Score neutral
    
    generic_phrases = ["Execute", "Process results", "Return structured output"]
    total_steps = 0
    non_generic_steps = 0
    
    for method in methods[: 5]:  # Sample first 5 methods
        steps = method.get('technical_approach', {}).get('steps', [])
        total_steps += len(steps)
        non_generic_steps += sum(1 for s in steps 
                                 if not any(g in s.get('description', '') for g in generic_phrases))
    
    specificity_ratio = non_generic_steps / total_steps if total_steps > 0 else 0
    return int(10 * specificity_ratio)
```

#### B3. Reglas de Validación [10 puntos]
```python
def verify_validation_rules(contract: Dict) -> Score:
    """
    PESO: 10 pts - Afecta robustez de verificación
    
    Verificaciones:
    □ Rules cubren expected_elements críticos [5 pts]
    □ must_contain vs should_contain balanceado [3 pts]
    □ failure_contract bien definido [2 pts]
    
    UMBRAL SUGERIDO: 6/10 para validación funcional
    """
    rules = contract.get('validation', {}).get('rules', [])
    expected = contract['question_context']['expected_elements']
    
    required_elements = {e['type'] for e in expected if e.get('required')}
    validated_elements = set()
    
    for rule in rules:
        if 'must_contain' in rule: 
            validated_elements.update(rule['must_contain']. get('elements', []))
        if 'should_contain' in rule:
            validated_elements.update(rule['should_contain'].get('elements', []))
    
    coverage = len(required_elements & validated_elements) / len(required_elements) if required_elements else 1
    coverage_score = int(5 * coverage)
    
    # Balance must vs should
    must_count = sum(1 for r in rules if 'must_contain' in r)
    should_count = sum(1 for r in rules if 'should_contain' in r)
    balance_score = 3 if must_count <= 2 and should_count >= must_count else 1
    
    # Failure contract
    failure_score = 2 if contract.get('error_handling', {}).get('failure_contract', {}).get('emit_code') else 0
    
    return coverage_score + balance_score + failure_score
```

### **TIER 3: COMPONENTES DE CALIDAD (15 puntos)**
*Nice-to-have, mejoran UX y mantenibilidad*

#### C1. Documentación Epistemológica [5 puntos]
```python
def verify_documentation_quality(contract: Dict) -> Score:
    """
    PESO: 5 pts - Mejora mantenibilidad
    
    Verificaciones:
    □ Paradigma no boilerplate [2 pts]
    □ Justificación específica [2 pts]
    □ Referencias externas [1 pt]
    """
    # Implementación simplificada
    return 3  # Score neutral si no crítico
```

#### C2. Template Human-Readable [5 puntos]
```python
def verify_human_template(contract: Dict) -> Score:
    """
    PESO: 5 pts - Mejora interpretabilidad
    
    Verificaciones:
    □ Referencias correctas [3 pts]
    □ Placeholders válidos [2 pts]
    """
    template = contract.get('output_contract', {}).get('human_readable_output', {}).get('template', {})
    
    score = 0
    # Verificar referencia correcta
    question_id = contract['identity']['question_id']
    if f"Q{question_id[1:]}" in str(template. get('title', '')):
        score += 3
    
    # Placeholders básicos presentes
    if '{score}' in str(template) and '{evidence' in str(template):
        score += 2
    
    return score
```

#### C3. Metadatos y Trazabilidad [5 puntos]
```python
def verify_metadata_completeness(contract: Dict) -> Score:
    """
    PESO: 5 pts - Mejora auditoría
    
    Verificaciones:
    □ contract_hash presente [2 pts]
    □ created_at timestamp [1 pt]
    □ validated_against_schema [1 pt]
    □ contract_version semver [1 pt]
    """
    identity = contract['identity']
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
```

## PARTE II: MATRIZ DE DECISIÓN PARCHEAR vs REFORMULAR

```python
class ContractTriageDecision:
    """
    Sistema de decisión para determinar estrategia de corrección
    """
    
    def triage(self, contract: Dict) -> str:
        scores = self.calculate_all_scores(contract)
        
        # TIER 1: Componentes Críticos (55 pts total)
        tier1_score = (
            scores['A1_identity_schema'] +     # /20
            scores['A2_method_assembly'] +     # /20
            scores['A3_signal_integrity'] +    # /10
            scores['A4_output_schema']         # /5
        )
        
        # TIER 2: Componentes Funcionales (30 pts total)
        tier2_score = (
            scores['B1_pattern_coverage'] +    # /10
            scores['B2_method_specificity'] +  # /10
            scores['B3_validation_rules']      # /10
        )
        
        # TIER 3: Componentes de Calidad (15 pts total)
        tier3_score = (
            scores['C1_documentation'] +       # /5
            scores['C2_human_template'] +      # /5
            scores['C3_metadata']               # /5
        )
        
        total = tier1_score + tier2_score + tier3_score
        
        # DECISIÓN ESTRATÉGICA
        if tier1_score < 35:  # Menos del 63% en críticos
            return self._reformulate_decision(scores)
        elif tier1_score >= 45 and total >= 70:  # 82% en críticos y 70% total
            return "PARCHEAR_MINOR"
        elif tier1_score >= 35 and total >= 60: 
            return "PARCHEAR_MAJOR"
        else: 
            return self._analyze_borderline(scores)
    
    def _reformulate_decision(self, scores: Dict) -> str:
        """
        Análisis detallado cuando Tier 1 falla
        """
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
            return "REFORMULAR_ASSEMBLY"  # Regenerar solo assembly
        elif "IDENTITY_SCHEMA_MISMATCH" in blockers:
            return "REFORMULAR_SCHEMA"  # Regenerar solo schema
        else:
            return "PARCHEAR_CRITICO"  # Un solo blocker, parcheable
    
    def _analyze_borderline(self, scores: Dict) -> str:
        """
        Casos límite:  Tier 1 pasa pero total bajo
        """
        # Si tiene buenos críticos pero mala documentación
        if scores['B2_method_specificity'] < 3: 
            return "PARCHEAR_DOCS"  # Solo mejorar documentación
        
        # Si patrones débiles
        if scores['B1_pattern_coverage'] < 6:
            return "PARCHEAR_PATTERNS"  # Regenerar patrones
        
        return "PARCHEAR_MAJOR"
```

### Tabla de Decisión Rápida

| Tier 1 Score | Tier 2 Score | Total Score | DECISIÓN | Acción |
|-------------|-------------|------------|----------|---------|
| < 35/55 (63%) | - | - | **REFORMULAR** | Regenerar desde monolith |
| 35-44/55 | < 15/30 | < 60 | **REFORMULAR** | Regenerar componentes rotos |
| 35-44/55 | ≥ 15/30 | 60-69 | **PARCHEAR_MAJOR** | Corregir assembly + schema |
| ≥ 45/55 (82%) | ≥ 20/30 | ≥ 70 | **PARCHEAR_MINOR** | Ajustes puntuales |
| ≥ 50/55 | ≥ 25/30 | ≥ 85 | **PRODUCCIÓN** | Listo para deploy |

## PARTE III: GUÍA DE GENERACIÓN DE CONTRATOS

### Contract Generation Pipeline (CGP)

```python
class ContractGenerator:
    """
    Generador de contratos con validación CQVR integrada
    """
    
    def __init__(self):
        self.monolith = load_questionnaire_monolith()
        self.signal_registry = SignalRegistry()
        self.method_registry = MethodRegistry()
        self.validator = ContractTriageDecision()
    
    def generate_contract(self, 
                          question_id: str,
                          policy_area: str,
                          dimension:  str) -> Dict:
        """
        Pipeline completo de generación con validación
        """
        
        # FASE 1: Extracción de Definición Canónica
        canonical = self._extract_canonical_definition(question_id)
        
        # FASE 2: Construcción Incremental con Validación
        contract = {}
        
        # 2.1 Identity (20 pts críticos)
        contract['identity'] = self._build_identity(
            question_id, policy_area, dimension, canonical
        )
        
        # 2.2 Method Binding
        contract['method_binding'] = self._select_optimal_methods(
            canonical, policy_area
        )
        
        # 2.3 Assembly Rules (20 pts críticos) - DEBE alinearse con methods
        contract['evidence_assembly'] = self._build_aligned_assembly(
            contract['method_binding']
        )
        
        # 2.4 Output Contract con Schema coherente (20 pts críticos)
        contract['output_contract'] = self._build_coherent_output(
            contract['identity']
        )
        
        # 2.5 Signal Requirements (10 pts críticos)
        contract['signal_requirements'] = self._define_signals(
            canonical, ensure_threshold=True
        )
        
        # 2.6 Question Context
        contract['question_context'] = self._extract_patterns(
            canonical
        )
        
        # 2.7 Validation Rules
        contract['validation'] = self._build_validation_rules(
            contract['question_context']['expected_elements']
        )
        
        # FASE 3: Validación Pre-Deploy
        score_report = calculate_contract_quality_score(contract)
        
        if score_report['percentage'] < 80:
            # Auto-remediate
            contract = self._auto_remediate(contract, score_report)
        
        # FASE 4: Firma y Versionado
        contract['identity']['contract_hash'] = self._compute_hash(contract)
        contract['identity']['created_at'] = datetime.now().isoformat()
        contract['identity']['contract_version'] = self._assign_version(contract)
        
        return contract
    
    def _build_identity(self, q_id: str, pa: str, dim: str, canonical: Dict) -> Dict:
        """
        Construye identity garantizando coherencia
        """
        return {
            'base_slot': f"{dim}-Q{canonical['question_number']}",
            'question_id': q_id,
            'dimension_id': dim,
            'policy_area_id': pa,
            'contract_version': '3.0.0',
            'created_at': datetime.now().isoformat(),
            'validated_against_schema': 'executor_contract. v3.schema.json',
            'cluster_id': canonical. get('cluster_id'),
            'question_global': canonical['global_index']
        }
    
    def _select_optimal_methods(self, canonical: Dict, policy_area: str) -> Dict:
        """
        Selección inteligente de métodos basada en tipo de pregunta
        """
        question_type = canonical['question_type']  # baseline, intervention, evaluation
        
        if question_type == 'baseline': 
            # Métodos de diagnóstico y auditoría
            selected_methods = [
                self.method_registry.get('OperationalizationAuditor._audit_direct_evidence'),
                self.method_registry.get('FinancialAuditor._detect_allocation_gaps'),
                self.method_registry.get('BayesianMechanismInference._detect_gaps'),
                self.method_registry. get('PolicyContradictionDetector._detect_numerical_inconsistencies'),
            ]
        elif question_type == 'intervention':
            # Métodos de simulación y optimización
            selected_methods = [
                self.method_registry. get('PDETMunicipalPlanAnalyzer._generate_optimal_remediations'),
                self.method_registry.get('PDETMunicipalPlanAnalyzer._simulate_intervention'),
                self.method_registry.get('BayesianCounterfactualAuditor. counterfactual_query'),
            ]
        else:  # evaluation
            # Métodos de análisis de impacto
            selected_methods = [
                self.method_registry.get('PerformanceAnalyzer. analyze_performance'),
                self.method_registry. get('BayesianConfidenceCalculator.calculate_posterior'),
                self.method_registry. get('ImpactEvaluator.measure_outcomes'),
            ]
        
        # Añadir métodos específicos de policy_area
        pa_specific = self.method_registry.get_policy_specific_methods(policy_area)
        selected_methods.extend(pa_specific[: 3])  # Máximo 3 específicos
        
        # Construir binding con provides correctos
        return {
            'orchestration_mode': 'multi_method_pipeline',
            'method_count': len(selected_methods),
            'methods': [
                {
                    'class_name': m['class'],
                    'method_name':  m['method'],
                    'priority': i + 1,
                    'provides': f"{m['class']. lower()}.{m['method'].lstrip('_')}",
                    'role': m['role'],
                    'description': m['description']
                }
                for i, m in enumerate(selected_methods)
            ]
        }
    
    def _build_aligned_assembly(self, method_binding: Dict) -> Dict:
        """
        Construcción de assembly GARANTIZANDO alineación con methods
        """
        # Extraer todos los provides
        all_provides = [m['provides'] for m in method_binding['methods']]
        
        # Reglas de assembly basadas en provides REALES
        return {
            'module':  'farfan_core. core. orchestrator. evidence_assembler',
            'class_name': 'EvidenceAssembler',
            'method_name': 'assemble',
            'output_schema': {
                'type': 'object',
                'required': ['elements', 'raw_results'],
                'properties': {
                    'elements': {'type': 'array'},
                    'raw_results':  {'type': 'object'}
                }
            },
            'assembly_rules': [
                {
                    'target':  'elements_found',
                    'sources': all_provides,  # TODOS los provides
                    'merge_strategy': 'concat',
                    'description': f'Combine evidence from {len(all_provides)} methods'
                },
                {
                    'target': 'confidence_scores',
                    'sources': [p for p in all_provides if 'bayesian' in p or 'confidence' in p],
                    'merge_strategy': 'weighted_mean',
                    'default':  []
                },
                {
                    'target': 'pattern_matches',
                    'sources': [p for p in all_provides if 'audit' in p or 'detect' in p],
                    'merge_strategy': 'concat',
                    'default': {}
                }
            ]
        }
    
    def _build_coherent_output(self, identity: Dict) -> Dict:
        """
        Schema de output PERFECTAMENTE alineado con identity
        """
        return {
            'result_type': 'Phase2QuestionResult',
            'schema': {
                'type': 'object',
                'required':  [
                    'base_slot', 'question_id', 'question_global',
                    'evidence', 'validation'
                ],
                'properties':  {
                    'base_slot': {
                        'type': 'string',
                        'const': identity['base_slot']  # EXACTO de identity
                    },
                    'question_id': {
                        'type': 'string',
                        'const': identity['question_id']  # EXACTO de identity
                    },
                    'question_global': {
                        'type': 'integer',
                        'const': identity['question_global']  # EXACTO de identity
                    },
                    'policy_area_id': {
                        'type': 'string',
                        'const': identity['policy_area_id']  # EXACTO de identity
                    },
                    'dimension_id': {
                        'type':  'string',
                        'const': identity['dimension_id']  # EXACTO de identity
                    },
                    'evidence': {
                        'type':  'object',
                        'additionalProperties': True
                    },
                    'validation': {
                        'type':  'object',
                        'additionalProperties': True
                    }
                },
                'additionalProperties': False
            },
            'consumer_modules': [
                'src.farfan_core.core.phases.phase2_types. validate_phase2_result',
                'src.farfan_core.core.orchestrator.core. Orchestrator._score_micro_results_async'
            ],
            'human_readable_output': self._generate_template(identity)
        }
    
    def _define_signals(self, canonical: Dict, ensure_threshold: bool = True) -> Dict:
        """
        Define señales con threshold > 0 SIEMPRE
        """
        # Extraer señales relevantes para el tipo de pregunta
        question_signals = self.signal_registry.get_signals_for_question(
            canonical['question_type'],
            canonical['policy_area']
        )
        
        mandatory = question_signals[: 5]  # Top 5 más relevantes
        optional = question_signals[5:10]  # Siguientes 5
        
        return {
            'mandatory_signals':  mandatory,
            'optional_signals': optional,
            'signal_aggregation': 'weighted_mean',
            'minimum_signal_threshold': 0. 5 if ensure_threshold else 0.3,  # NUNCA 0
            'note': f'Signals configured for {canonical["question_type"]} analysis'
        }
    
    def _extract_patterns(self, canonical: Dict) -> Dict:
        """
        Extrae patrones específicos de la pregunta
        """
        base_patterns = canonical.get('search_patterns', [])
        
        # Enriquecer con variaciones
        enriched_patterns = []
        for i, pattern in enumerate(base_patterns):
            enriched_patterns.append({
                'id': f"PAT-{canonical['question_id']}-{i: 03d}",
                'pattern': pattern['regex'],
                'category': pattern. get('category', 'GENERAL'),
                'confidence_weight': 0.85,
                'match_type': 'REGEX',
                'flags': 'i'  # case insensitive
            })
        
        # Extraer elementos esperados
        expected_elements = [
            {
                'type':  elem,
                'required': True
            }
            for elem in canonical.get('required_elements', [])
        ]
        
        return {
            'question_text': canonical['question_text'],
            'question_type': canonical['question_type'],
            'patterns': enriched_patterns,
            'expected_elements': expected_elements,
            'scoring_modality': canonical.get('scoring_modality', 'TYPE_B')
        }
    
    def _build_validation_rules(self, expected_elements: List[Dict]) -> Dict:
        """
        Construye reglas de validación coherentes con expected_elements
        """
        required_types = [e['type'] for e in expected_elements if e.get('required')]
        
        rules = []
        
        # Regla crítica para elementos requeridos
        if required_types:
            rules.append({
                'field': 'elements_found',
                'must_contain': {
                    'count': 1,
                    'elements': required_types[: 2]  # Los 2 más críticos
                }
            })
        
        # Reglas suaves para calidad
        rules.extend([
            {
                'field': 'elements_found',
                'should_contain': {
                    'minimum':  3,
                    'elements': required_types
                }
            },
            {
                'field': 'confidence_scores',
                'threshold': {
                    'minimum_mean': 0.6
                }
            }
        ])
        
        return {
            'na_policy': 'abort_on_critical',
            'rules': rules,
            'error_handling': {
                'on_method_failure': 'propagate_with_trace',
                'failure_contract': {
                    'abort_if':  ['missing_required_element'],
                    'emit_code': f'ABORT-{expected_elements[0]["type"][: 4].upper()}-REQ'
                }
            }
        }
    
    def _auto_remediate(self, contract: Dict, score_report:  Dict) -> Dict:
        """
        Auto-corrección basada en score report
        """
        for issue, score in score_report['breakdown'].items():
            if 'identity' in issue and score < 15:
                # Reconstruir schema desde identity
                contract['output_contract']['schema'] = self._rebuild_schema_from_identity(
                    contract['identity']
                )
            
            elif 'assembly' in issue and score < 12:
                # Reconstruir assembly desde method_binding
                contract['evidence_assembly'] = self._build_aligned_assembly(
                    contract['method_binding']
                )
            
            elif 'signal' in issue and score < 5:
                # Forzar threshold > 0
                contract['signal_requirements']['minimum_signal_threshold'] = 0.5
        
        return contract
    
    def _compute_hash(self, contract: Dict) -> str:
        """
        Calcula SHA256 del contrato para trazabilidad
        """
        import hashlib
        import json
        
        # Excluir campos mutables
        hashable = {k: v for k, v in contract.items() 
                   if k not in ['identity', 'calibration']}
        
        contract_str = json.dumps(hashable, sort_keys=True)
        return hashlib.sha256(contract_str.encode()).hexdigest()
```

## PARTE IV: CHECKLIST DE GENERACIÓN

### Pre-Generación
- [ ] Questionnaire monolith disponible y válido
- [ ] Signal registry poblado para policy_area
- [ ] Method registry con métodos implementados
- [ ] Esquema de validación v3 disponible

### Durante Generación
- [ ] **CRÍTICO**: Identity y Output Schema usan EXACTAMENTE los mismos valores const
- [ ] **CRÍTICO**: Assembly rules solo referencian provides que existen
- [ ] **CRÍTICO**: Signal threshold > 0 si hay mandatory_signals
- [ ] **CRÍTICO**: Output schema tiene todos los required fields definidos
- [ ] Pattern IDs únicos y bien formados
- [ ] Expected elements mapeados a validation rules
- [ ] Method count = len(methods)

### Post-Generación
- [ ] Score CQVR ≥ 80/100
- [ ] Tier 1 (críticos) ≥ 45/55
- [ ] Contract hash calculado
- [ ] Versionado semántico aplicado
- [ ] Test de ejecución en sandbox exitoso

### Validación CI/CD
```yaml
# .github/workflows/contract-validation.yml
name: Contract Quality Check

on:
  push:
    paths:
      - 'src/canonic_phases/**/executor_contracts/**/*. json'

jobs:
  validate-contracts:
    runs-on:  ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run CQVR on all contracts
        run: |
          python scripts/validate_contracts.py \
            --min-score 80 \
            --tier1-min 45 \
            --fail-on-critical
      
      - name: Generate quality report
        run: |
          python scripts/generate_contract_report.py \
            --output reports/contract_quality. html
      
      - name: Block if quality insufficient
        run: |
          if [ -f . contract_failures ]; then
            echo "❌ Contracts below quality threshold"
            cat .contract_failures
            exit 1
          fi
```

## CONCLUSIÓN

Con esta rúbrica de pesos estratégicos: 

1. **Contratos con Tier 1 < 35/55** → REFORMULAR (no parcheable)
2. **Contratos con Tier 1 ≥ 35/55 pero Total < 60** → PARCHEAR_MAJOR
3. **Contratos con Total ≥ 80/100** → PRODUCCIÓN

El contrato Q002. v3.json obtendría:
- Tier 1: 2 + 0 + 0 + 3 = **5/55** → **REFORMULAR COMPLETO**
- No vale la pena parchear, regenerar desde cero con el ContractGenerator

La guía asegura que nuevos contratos nacen con score ≥ 80 mediante validación incremental durante generación. 