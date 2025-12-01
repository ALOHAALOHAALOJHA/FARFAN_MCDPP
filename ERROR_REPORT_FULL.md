# Detailed Syntax Error Report

Total Errors Found: 239

## Error 1
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 60
- **Problem**: Syntax error involving get_parameter_loader().
```python
59: from transformers import pipeline
60: from farfan_core import get_parameter_loader  <-- ERROR
61: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 2
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 342
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
341:             for idx, table in enumerate(lattice_tables):
342:                 if table.parsing_report['accuracy'] > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_spanish_stopwords").get("auto_param_L342_54", 0.7):  <-- ERROR
343:                     all_tables.append(ExtractedTable(
```

## Error 3
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 360
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
359:             for idx, table in enumerate(stream_tables):
360:                 if table.parsing_report['accuracy'] > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_spanish_stopwords").get("auto_param_L360_54", 0.6):  <-- ERROR
361:                     all_tables.append(ExtractedTable(
```

## Error 4
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 384
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
383:                         extraction_method='tabula',
384:                         confidence_score = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_spanish_stopwords").get("confidence_score", 0.6) # Refactored  <-- ERROR
385:                     ))
```

## Error 5
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 466
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
465:                 continue
466:             duplicates = (similarities[i] > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._deduplicate_tables").get("auto_param_L466_44", 0.85)).nonzero(as_tuple=True)[0].tolist()  <-- ERROR
467:             best_idx = max(duplicates, key=lambda idx: tables[idx].confidence_score)
```

## Error 6
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 486
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
485:         embeddings = self.semantic_model.encode(features, convert_to_tensor=False)
486:         clustering = DBSCAN(eps=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._deduplicate_tables").get("auto_param_L486_32", 0.3), min_samples=2, metric='cosine').fit(embeddings)  <-- ERROR
487: 
```

## Error 7
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 596
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
595:                         execution_percentage=None,
596:                         risk_level = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._extract_financial_amounts").get("risk_level", 0.0) # Refactored  <-- ERROR
597:                     ))
```

## Error 8
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 661
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
660:                     execution_percentage=None,
661:                     risk_level = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._extract_from_budget_table").get("risk_level", 0.0) # Refactored  <-- ERROR
662:                 ))
```

## Error 9
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 678
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
677:         if total == 0:
678:             return {'distribution': {}, 'diversity_index': get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._analyze_funding_sources").get("auto_param_L678_59", 0.0)}  <-- ERROR
679: 
```

## Error 10
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 687
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
686:             'max_diversity': np.log(len(source_distribution)),
687:             'dependency_risk': get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._analyze_funding_sources").get("auto_param_L687_31", 1.0) - (diversity / np.log(max(len(source_distribution), 2)))  <-- ERROR
688:         }
```

## Error 11
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 696
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
695:         if not indicators:
696:         diversity_score = min(funding_sources.get('diversity_index', 0) / funding_sources.get('max_diversity', 1), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._assess_financial_sustainability").get("auto_param_L696_115", 1.0))  <-- ERROR
697: 
```

## Error 12
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 704
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
703:         total = sum(distribution.values())
704:         sustainability = (diversity_score * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._assess_financial_sustainability").get("auto_param_L704_44", 0.3) + own_resources * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._assess_financial_sustainability").get("auto_param_L704_66", 0.4) + (1 - pdet_risk) * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._assess_financial_sustainability").get("auto_param_L704_90", 0.3))  <-- ERROR
705:         return float(sustainability)
```

## Error 13
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 716
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
715:             'sustainability': sustainability,
716:             'dependency': funding_sources.get('dependency_risk', get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._bayesian_risk_inference").get("auto_param_L716_65", 0.5))  <-- ERROR
717:         }
```

## Error 14
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 723
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
722:             base_risk = pm.Beta('base_risk', alpha=2, beta=5)
723:             dependency_effect = pm.Normal('dependency_effect', mu=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._bayesian_risk_inference").get("auto_param_L723_66", 0.5), sigma=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._bayesian_risk_inference").get("auto_param_L723_77", 0.15))  <-- ERROR
724: 
```

## Error 15
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 758
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
757:     def _interpret_risk(self, risk: float) -> str:
758:         elif risk < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._interpret_risk").get("auto_param_L758_20", 0.8):  <-- ERROR
759:             return "Riesgo alto - Vulnerabilidades significativas"
```

## Error 16
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 804
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
803:                 for entity in ner_results:
804:                     if entity['entity_group'] in ['ORG', 'PER'] and entity['score'] > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._extract_entities_ner").get("auto_param_L804_86", 0.7):  <-- ERROR
805:                         entities.append(ResponsibleEntity(
```

## Error 17
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 838
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
837:                     entity_type=entity_type,
838:                     specificity_score=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._extract_entities_syntax").get("auto_param_L838_38", 0.6),  <-- ERROR
839:                     mentioned_count=1,
```

## Error 18
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 884
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
883:                     entity_type=self._classify_entity_type(name),
884:                     specificity_score=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._extract_from_responsibility_tables").get("auto_param_L884_38", 0.8),  <-- ERROR
885:                     mentioned_count=1,
```

## Error 19
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 901
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
900: 
901:         similarity_threshold = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._consolidate_entities").get("similarity_threshold", 0.85) # Refactored  <-- ERROR
902:         clustering = AgglomerativeClustering(
```

## Error 20
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 936
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
935: 
936:             propn_score = min(propn_count / 3, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_entity_specificity").get("auto_param_L936_47", 1.0))  <-- ERROR
937: 
```

## Error 21
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 943
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
942:             inst_score = float(any(word in entity.name.lower() for word in institutional_words))
943:             final_score = (length_score * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_entity_specificity").get("auto_param_L943_42", 0.2) + propn_score * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_entity_specificity").get("auto_param_L943_62", 0.3) + inst_score * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_entity_specificity").get("auto_param_L943_81", 0.3) + mention_score * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_entity_specificity").get("auto_param_L943_103", 0.2))  <-- ERROR
944: 
```

## Error 22
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 969
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
968:                 'type': node.node_type,
969:                 'budget': float(node.associated_budget) if node.associated_budget else get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.construct_causal_dag").get("auto_param_L969_87", 0.0),  <-- ERROR
970:                 'evidence': node.evidence_strength
```

## Error 23
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 974
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
973:         for edge in edges:
974:             if edge.probability > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.construct_causal_dag").get("auto_param_L974_34", 0.3):  <-- ERROR
975:                 G.add_edge(edge.source, edge.target, **{
```

## Error 24
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1015
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1014:                     temporal_lag=self.context.PDET_THEORY_OF_CHANGE[pillar]['lag_years'],
1015:                     evidence_strength=min(len(mentions) / 5, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_nodes").get("auto_param_L1015_61", 1.0))  <-- ERROR
1016:                 )
```

## Error 25
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1031
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1030:                         temporal_lag=0,
1031:                         evidence_strength=min(len(outcome_mentions) / 3, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_nodes").get("auto_param_L1031_73", 1.0))  <-- ERROR
1032:                     )
```

## Error 26
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1043
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1042:                         temporal_lag=0,
1043:                         evidence_strength=min(len(mediator_mentions) / 2, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_nodes").get("auto_param_L1043_74", 1.0))  <-- ERROR
1044:                     )
```

## Error 27
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1062
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1061: 
1062:             if similarity > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._find_semantic_mentions").get("auto_param_L1062_28", 0.5):  <-- ERROR
1063:                 mentions.append(sentence)
```

## Error 28
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1168
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1167:                         mechanism="Mecanismo según teoría PDET",
1168:                         probability = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_edges").get("probability", 0.8) # Refactored  <-- ERROR
1169:                     ))
```

## Error 29
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1180
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1179:                                 mechanism=f"Mediado por {mediator}",
1180:                                 probability = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_edges").get("probability", 0.7) # Refactored  <-- ERROR
1181:                             ))
```

## Error 30
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1201
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1200:                     if existing:
1201:                         existing.probability = min(existing.probability + get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_edges").get("auto_param_L1201_74", 0.2), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_edges").get("auto_param_L1201_79", 1.0))  <-- ERROR
1202:                         existing.evidence_quotes.append(match.group(0)[:200])
```

## Error 31
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1210
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1209:                             evidence_quotes=[match.group(0)[:200]],
1210:                             probability = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._identify_causal_edges").get("probability", 0.6) # Refactored  <-- ERROR
1211:                         ))
```

## Error 32
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1225
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1224:         best_match = None
1225:         best_similarity = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._match_text_to_node").get("best_similarity", 0.0) # Refactored  <-- ERROR
1226: 
```

## Error 33
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1235
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1234: 
1235:             if similarity > best_similarity and similarity > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._match_text_to_node").get("auto_param_L1235_61", 0.4):  <-- ERROR
1236:                 best_similarity = similarity
```

## Error 34
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1261
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1260:             if cooccurrence_count > 0:
1261:                 edge.probability = min(edge.probability + boost, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._refine_edge_probabilities").get("auto_param_L1261_65", 1.0))  <-- ERROR
1262: 
```

## Error 35
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1270
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1269:                 cycle = nx.find_cycle(G)
1270:                 weakest_edge = min(cycle, key=lambda e: G[e[0]][e[1]].get('probability', get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._break_cycles").get("auto_param_L1270_89", 0.5)))  <-- ERROR
1271:                 G.remove_edge(weakest_edge[0], weakest_edge[1])
```

## Error 36
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1325
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1324:         treatment_node = dag.nodes[treatment]
1325:         budget_value = float(treatment_node.associated_budget) if treatment_node.associated_budget else get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_effect_bayesian").get("auto_param_L1325_104", 0.0)  <-- ERROR
1326: 
```

## Error 37
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1335
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1334:                 path_name = '->'.join([p[:15] for p in path])
1335:                 indirect_eff = pm.Normal(f'indirect_{path_name}', mu=prior_mean * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_effect_bayesian").get("auto_param_L1335_82", 0.5), sigma=prior_sd * 1.5)  <-- ERROR
1336:                 indirect_effects.append(indirect_eff)
```

## Error 38
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1340
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1339:                 budget_adjustment = pm.Deterministic('budget_adjustment', pm.math.log1p(budget_value / 1e9))
1340:                 adjusted_direct = direct_effect * (1 + budget_adjustment * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_effect_bayesian").get("auto_param_L1340_75", 0.1))  <-- ERROR
1341:             else:
```

## Error 39
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1355
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1354:             evidence_strength = treatment_node.evidence_strength * dag.nodes[outcome].evidence_strength
1355:             trace = pm.sample(1500, tune=800, cores=1, return_inferencedata=True, progressbar=False, target_accept=get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_effect_bayesian").get("auto_param_L1355_115", 0.9))  <-- ERROR
1356: 
```

## Error 40
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1363
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1362:         prob_positive = float(np.mean(total_samples > 0))
1363:         prob_significant = float(np.mean(np.abs(total_samples) > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_effect_bayesian").get("auto_param_L1363_65", 0.1)))  <-- ERROR
1364: 
```

## Error 41
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1391
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1390:         effect_priors = {
1391:                                                                                                             get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_prior_effect").get("auto_param_L1391_108", 0.17)),  <-- ERROR
1392:         }
```

## Error 42
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1397
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1396: 
1397:         return (get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_prior_effect").get("auto_param_L1397_16", 0.2), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._get_prior_effect").get("auto_param_L1397_21", 0.25))  <-- ERROR
1398: 
```

## Error 43
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1438
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1437:         current_budgets = {
1438:             node: float(dag.nodes[node].associated_budget) if dag.nodes[node].associated_budget else get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_counterfactuals").get("auto_param_L1438_101", 0.0)  <-- ERROR
1439:             for node in pillar_nodes
```

## Error 44
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1474
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1473: 
1474:             intervention_3 = {node: budget * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_counterfactuals").get("auto_param_L1474_45", 0.7) for node, budget in current_budgets.items()}  <-- ERROR
1475:             if best_pillar in intervention_3:
```

## Error 45
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1504
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1503: 
1504:             variance_sum = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._simulate_intervention").get("variance_sum", 0.0) # Refactored  <-- ERROR
1505: 
```

## Error 46
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1518
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1517:                 current_budget = float(dag.nodes[treatment].associated_budget) if dag.nodes[
1518:                 effect_multiplier = np.log1p(budget_multiplier) / np.log1p(get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._simulate_intervention").get("auto_param_L1518_75", 1.0))  <-- ERROR
1519: 
```

## Error 47
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1565
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1564: 
1565:         significant_outcomes = [(o, p) for o, p in probabilities.items() if p > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._generate_scenario_narrative").get("auto_param_L1565_80", 0.6)]  <-- ERROR
1566:         significant_outcomes.sort(key=lambda x: -x[1])
```

## Error 48
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1612
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1611:         if effect.posterior_mean <= 0:
1612:             return get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._compute_e_value").get("auto_param_L1612_19", 1.0)  <-- ERROR
1613: 
```

## Error 49
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1616
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1615:         if rr <= 1:
1616:             return get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._compute_e_value").get("auto_param_L1616_19", 1.0)  <-- ERROR
1617:         e_value = rr + np.sqrt(rr * (rr - 1))
```

## Error 50
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1625
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1624:         Robustness Value: percentil de la distribución posterior que cruza cero
1625:         Valores altos (>get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._compute_robustness_value").get("auto_param_L1625_24", 0.95)) indican alta robustez  <-- ERROR
1626:         """
```

## Error 51
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1630
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1629:         if ci_lower > 0 or ci_upper < 0:
1630:             return get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._compute_robustness_value").get("auto_param_L1630_19", 1.0)  <-- ERROR
1631: 
```

## Error 52
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1637
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1636:         if width == 0:
1637:         return float(min(robustness, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._compute_robustness_value").get("auto_param_L1637_37", 1.0)))  <-- ERROR
1638: 
```

## Error 53
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1647
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1646: 
1647:         elif e_value > 1.2 and robustness > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._interpret_sensitivity").get("auto_param_L1647_44", 0.4):  <-- ERROR
1648:             return "Efecto sensible - Alta vulnerabilidad a confounding"
```

## Error 54
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1675
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1674: 
1675:         weights = np.array([get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_28", 0.20), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_34", 0.15), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_40", 0.15), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_46", 0.10), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_52", 0.20), get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1675_58", 0.20)])  <-- ERROR
1676:         scores = np.array([
```

## Error 55
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1694
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1693: 
1694:         print(f" ✓ Score final: {overall_score:.2f}/1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.calculate_quality_score").get("auto_param_L1694_53", 0.0)")  <-- ERROR
1695: 
```

## Error 56
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1716
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1715:         if budget == 0:
1716:         budget_score = min(np.log10(float(budget)) / 12, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_financial_component").get("auto_param_L1716_57", 1.0)) * 3.0  <-- ERROR
1717: 
```

## Error 57
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1720
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1719:         max_diversity = financial_analysis['funding_sources'].get('max_diversity', 1)
1720:         diversity_score = (diversity / max(max_diversity, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_financial_component").get("auto_param_L1720_58", 0.1))) * 3.0  <-- ERROR
1721: 
```

## Error 58
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1728
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1727: 
1728:         return float(min(budget_score + diversity_score + sustainability_score + risk_score, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_financial_component").get("auto_param_L1728_94", 0.0)))  <-- ERROR
1729: 
```

## Error 59
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1744
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1743: 
1744:         completeness_score = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_indicators").get("completeness_score", 0.0) # Refactored  <-- ERROR
1745:         for table in indicator_tables:
```

## Error 60
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1760
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1759:         smart_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in smart_patterns)
1760:         smart_score = min(smart_count / 50, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_indicators").get("auto_param_L1760_44", 1.0)) * 3.0  <-- ERROR
1761: 
```

## Error 61
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1767
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1766: 
1767:         return float(min(completeness_score + smart_score + technical_score, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_indicators").get("auto_param_L1767_78", 0.0)))  <-- ERROR
1768: 
```

## Error 62
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1776
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1775: 
1776:         count_score = min(len(entities) / 15, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_responsibility_clarity").get("auto_param_L1776_46", 1.0)) * 3.0  <-- ERROR
1777: 
```

## Error 63
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1785
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1784: 
1785:         return float(min(count_score + specificity_score + institutional_score, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_responsibility_clarity").get("auto_param_L1785_81", 0.0)))  <-- ERROR
1786: 
```

## Error 64
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1798
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1797:         year_range = max(years) - min(years) if years else 0
1798:         range_score = min(year_range / 4, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_temporal_consistency").get("auto_param_L1798_42", 1.0)) * 3.0  <-- ERROR
1799: 
```

## Error 65
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1807
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1806:         term_count = sum(len(re.findall(rf'\b{term}\b', text, re.IGNORECASE)) for term in temporal_terms)
1807:         return float(min(range_score + cronograma_score + term_score, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_temporal_consistency").get("auto_param_L1807_71", 0.0)))  <-- ERROR
1808: 
```

## Error 66
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1828
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1827:         patr_mentions = len(re.findall(r'\bPATR\b', text, re.IGNORECASE))
1828:         explicit_score = min((pdet_explicit + patr_mentions) / 15, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_pdet_alignment").get("auto_param_L1828_67", 1.0)) * 3.0  <-- ERROR
1829: 
```

## Error 67
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1833
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1832: 
1833:         return float(min(coverage_score + explicit_score + table_score, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_pdet_alignment").get("auto_param_L1833_73", 0.0)))  <-- ERROR
1834: 
```

## Error 68
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1847
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1846: 
1847:             effect_quality = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_causal_coherence").get("effect_quality", 0.0) # Refactored  <-- ERROR
1848:         else:
```

## Error 69
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1858
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1857: 
1858:         return float(min(structure_score + effect_quality + connectivity, 1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._score_causal_coherence").get("auto_param_L1858_75", 0.0)))  <-- ERROR
1859: 
```

## Error 70
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1868
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1867:         for _ in range(n_bootstrap):
1868:             noise = np.random.normal(0, get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._estimate_score_confidence").get("auto_param_L1868_40", 0.5), size=len(scores))  <-- ERROR
1869:             noisy_scores = np.clip(scores + noise, 0, 10)
```

## Error 71
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1894
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1893:             data['node_type'] = data.get('type', 'unknown')
1894:             data['weight'] = data.get('probability', get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.export_causal_network").get("auto_param_L1894_53", 0.5))  <-- ERROR
1895:             data['edge_type'] = data.get('type', 'unknown')
```

## Error 72
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1910
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1909:         quality = analysis_results['quality_score']
1910:         report += f"**Score Global de Calidad:** {quality['overall_score']:.2f}/1get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_executive_report").get("auto_param_L1910_81", 0.0) "  <-- ERROR
1911:         report += f"(IC95%: [{quality['confidence_interval'][0]:.2f}, {quality['confidence_interval'][1]:.2f}])\n\n"
```

## Error 73
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 1944
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1943: 
1944:             significant_effects = [e for e in effects if e['probability_significant'] > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_executive_report").get("auto_param_L1944_88", 0.7)]  <-- ERROR
1945:             significant_effects.sort(key=lambda e: abs(e['posterior_mean']), reverse=True)
```

## Error 74
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2015
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2014:             fin = analysis_results['financial_analysis']
2015:             if fin['funding_sources'].get('dependency_risk', 0) > get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._generate_recommendations").get("auto_param_L2015_66", 0.6):  <-- ERROR
2016:                 recommendations.append(
```

## Error 75
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2021
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2020: 
2021:             if fin['sustainability_score'] < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._generate_recommendations").get("auto_param_L2021_45", 0.5):  <-- ERROR
2022:                 recommendations.append(
```

## Error 76
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2040
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2039:         if effects:
2040:             if len(weak_effects) > len(effects) * get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer._generate_recommendations").get("auto_param_L2040_50", 0.5):  <-- ERROR
2041:                 recommendations.append(
```

## Error 77
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2379
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2378:         # Check financial feasibility
2379:         if analysis_results.get('financial_feasibility', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2379_62", 0.7):  <-- ERROR
2380:             recommendations.append(
```

## Error 78
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2385
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2384:         # Check indicator quality
2385:         if analysis_results.get('indicator_quality', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2385_58", 0.7):  <-- ERROR
2386:             recommendations.append(
```

## Error 79
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2391
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2390:         # Check responsibility clarity
2391:         if analysis_results.get('responsibility_clarity', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2391_63", 0.7):  <-- ERROR
2392:             recommendations.append(
```

## Error 80
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2397
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2396:         # Check temporal consistency
2397:         if analysis_results.get('temporal_consistency', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2397_61", 0.7):  <-- ERROR
2398:             recommendations.append(
```

## Error 81
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2403
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2402:         # Check causal coherence
2403:         if analysis_results.get('causal_coherence', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2403_57", 0.7):  <-- ERROR
2404:             recommendations.append(
```

## Error 82
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2410
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2409:         if analysis_results.get('is_pdet_municipality', False):
2410:             if analysis_results.get('pdet_alignment', 0) < get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("auto_param_L2410_59", 0.7):  <-- ERROR
2411:                 recommendations.append(
```

## Error 83
- **File**: `farfan_core/farfan_core/analysis/financiero_viabilidad_tablas.py`
- **Line**: 2482
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2481:         language='es',
2482:         confidence_threshold = get_parameter_loader().get("farfan_core.analysis.financiero_viabilidad_tablas.PDETMunicipalPlanAnalyzer.generate_recommendations").get("confidence_threshold", 0.7) # Refactored  <-- ERROR
2483:     )
```

## Error 84
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 38
- **Problem**: Syntax error involving get_parameter_loader().
```python
37: from scipy import stats
38: from farfan_core import get_parameter_loader  <-- ERROR
39: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 85
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 115
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
114:                 rule=rule, passed=True, observed_value=value,
115:                 expected_value=None, violation_severity=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_range").get("auto_param_L115_56", 0.0), penalty_applied=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_range").get("auto_param_L115_77", 0.0)  <-- ERROR
116:             )
```

## Error 86
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 130
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
129:             if value < min_val:
130:         penalty = violation_severity * rule.penalty_factor if not passed else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_range").get("auto_param_L130_78", 0.0)  <-- ERROR
131: 
```

## Error 87
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 144
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
143:                 rule=rule, passed=True, observed_value=unit,
144:                 expected_value=None, violation_severity=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_unit").get("auto_param_L144_56", 0.0), penalty_applied=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_unit").get("auto_param_L144_77", 0.0)  <-- ERROR
145:             )
```

## Error 88
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 149
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
148:         passed = unit.lower() == rule.expected_unit.lower()
149:         penalty = violation_severity * rule.penalty_factor if not passed else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_unit").get("auto_param_L149_78", 0.0)  <-- ERROR
150: 
```

## Error 89
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 163
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
162:                 rule=rule, passed=True, observed_value=period,
163:                 expected_value=None, violation_severity=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_period").get("auto_param_L163_56", 0.0), penalty_applied=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_period").get("auto_param_L163_77", 0.0)  <-- ERROR
164:             )
```

## Error 90
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 168
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
167:         passed = period.lower() == rule.expected_period.lower()
168:         penalty = violation_severity * rule.penalty_factor if not passed else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_period").get("auto_param_L168_78", 0.0)  <-- ERROR
169: 
```

## Error 91
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 182
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
181:                 rule=rule, passed=True, observed_value=entity,
182:                 expected_value=None, violation_severity=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_entity").get("auto_param_L182_56", 0.0), penalty_applied=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_entity").get("auto_param_L182_77", 0.0)  <-- ERROR
183:             )
```

## Error 92
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 187
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
186:         passed = entity.lower() == rule.expected_entity.lower()
187:         penalty = violation_severity * rule.penalty_factor if not passed else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ReconciliationValidator.validate_entity").get("auto_param_L187_78", 0.0)  <-- ERROR
188: 
```

## Error 93
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 257
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
256:         Straw-in-wind: weak confirmation (LR ~ 2)
257:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ProbativeTest.calculate_likelihood_ratio").get("auto_param_L257_19", 1.0)  <-- ERROR
258: 
```

## Error 94
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 302
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
301:         # Ensure valid probability
302:         posterior = max(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianUpdater.update").get("auto_param_L302_24", 0.0), min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianUpdater.update").get("auto_param_L302_33", 1.0), posterior))  <-- ERROR
303: 
```

## Error 95
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 413
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
412:         if not scores or len(scores) < 2:
413:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_cv").get("auto_param_L413_19", 0.0)  <-- ERROR
414: 
```

## Error 96
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 419
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
418:         if mean_score == 0:
419:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_cv").get("auto_param_L419_19", 0.0)  <-- ERROR
420: 
```

## Error 97
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 428
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
427:         if not scores or len(scores) < 2:
428:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_max_gap").get("auto_param_L428_19", 0.0)  <-- ERROR
429: 
```

## Error 98
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 433
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
432: 
433:         return max(gaps) if gaps else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_max_gap").get("auto_param_L433_38", 0.0)  <-- ERROR
434: 
```

## Error 99
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 442
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
441:         if not scores or len(scores) < 2:
442:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_gini").get("auto_param_L442_19", 0.0)  <-- ERROR
443: 
```

## Error 100
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 470
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
469:         # Calculate penalties for each metric
470:         total_penalty = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.DispersionEngine.calculate_dispersion_penalty").get("auto_param_L470_28", 1.0), cv_penalty + gap_penalty + gini_penalty)  <-- ERROR
471: 
```

## Error 101
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 531
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
530:         peer_scores = [
531:             peer.scores.get(dimension, get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L531_39", 0.0))  <-- ERROR
532:             for peer in peer_contexts
```

## Error 102
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 543
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
542:                 target_score=target_score,
543:                 deviation_penalty=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L543_34", 0.0),  <-- ERROR
544:                 narrative="No peer data available for comparison"
```

## Error 103
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 549
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
548:         peer_mean = np.mean(peer_scores)
549:         peer_std = np.std(peer_scores, ddof=1) if len(peer_scores) > 1 else get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L549_76", 1.0)  <-- ERROR
550: 
```

## Error 104
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 559
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
558:         # Calculate percentile
559:         deviation_penalty = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L559_32", 0.5), deviation_penalty)  # Cap at get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L559_66", 0.5)  <-- ERROR
560: 
```

## Error 105
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 590
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
589:             performance = "significantly above"
590:         elif z_score > -get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L590_24", 0.5):  <-- ERROR
591:             performance = "comparable to"
```

## Error 106
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 604
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
603:         # Determine percentile description
604:         elif percentile >= get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.PeerCalibrator.__init__").get("auto_param_L604_27", 0.25):  <-- ERROR
605:             rank = "below median"
```

## Error 107
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 648
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
647:         micro_analyses: list[MicroLevelAnalysis],
648:         peer_penalty: float = get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L648_30", 0.0),  <-- ERROR
649:         additional_penalties: dict[str, float] | None = None
```

## Error 108
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 659
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
658:         if not micro_analyses:
659:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L659_19", 0.0)  <-- ERROR
660: 
```

## Error 109
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 675
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
674:         adjusted_posterior = raw_meso_posterior * (1 - total_penalty)
675:         adjusted_posterior = max(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L675_33", 0.0), min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L675_42", 1.0), adjusted_posterior))  <-- ERROR
676: 
```

## Error 110
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 711
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
710:                 f"{analysis.adjusted_score:.4f}",
711:                 f"{analysis.dispersion_metrics.get('gini', get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L711_59", 0.0)):.4f}"  <-- ERROR
712:             ])
```

## Error 111
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 732
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
731:     discrepancy: float
732:     severity: float  # get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L732_23", 0.0)-get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianRollUp.__init__").get("auto_param_L732_27", 1.0)  <-- ERROR
733:     description: str
```

## Error 112
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 757
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
756:             if discrepancy > self.discrepancy_threshold:
757:                 severity = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ContradictionScanner.__init__").get("auto_param_L757_31", 1.0), discrepancy / 2.0)  <-- ERROR
758: 
```

## Error 113
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 789
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
788:             if discrepancy > self.discrepancy_threshold:
789:                 severity = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ContradictionScanner.__init__").get("auto_param_L789_31", 1.0), discrepancy / 2.0)  <-- ERROR
790: 
```

## Error 114
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 812
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
811:         if not self.contradictions:
812:             return get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ContradictionScanner.calculate_contradiction_penalty").get("auto_param_L812_19", 0.0)  <-- ERROR
813: 
```

## Error 115
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 818
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
817:         avg_severity = np.mean([c.severity for c in self.contradictions])
818:         penalty = avg_severity * count_factor * get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ContradictionScanner.calculate_contradiction_penalty").get("auto_param_L818_48", 0.5)  # Max penalty get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.ContradictionScanner.calculate_contradiction_penalty").get("auto_param_L818_67", 0.5)  <-- ERROR
819: 
```

## Error 116
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 870
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
869:         # Penalty increases sharply below 70% coverage
870:         penalty = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L870_22", 1.0), penalty)  <-- ERROR
871: 
```

## Error 117
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 893
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
892:             return MacroLevelAnalysis(
893:                 adjusted_score=get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L893_31", 0.0),  <-- ERROR
894:                 cluster_scores={},
```

## Error 118
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 911
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
910:         dispersion_penalty, dispersion_metrics = dispersion_engine.calculate_dispersion_penalty(meso_scores)
911:         dispersion_score = get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L911_27", 1.0) - dispersion_penalty  <-- ERROR
912: 
```

## Error 119
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 919
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
918:         total_penalty = coverage_penalty + dispersion_penalty + contradiction_penalty
919:         total_penalty = min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L919_28", 1.0), total_penalty)  <-- ERROR
920: 
```

## Error 120
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 923
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
922:         adjusted_score = raw_overall * (1 - total_penalty)
923:         adjusted_score = max(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L923_29", 0.0), min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L923_38", 1.0), adjusted_score))  <-- ERROR
924: 
```

## Error 121
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 973
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
972: 
973:         if coverage_penalty > get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L973_30", 0.1):  <-- ERROR
974:             recommendations.append(
```

## Error 122
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 979
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
978: 
979:         if dispersion_penalty > get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L979_32", 0.1):  <-- ERROR
980:             recommendations.append(
```

## Error 123
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 985
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
984: 
985:         if contradiction_penalty > get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L985_35", 0.05):  <-- ERROR
986:             recommendations.append(
```

## Error 124
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 1038
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1037:                 f"{macro_analysis.adjusted_score:.4f}",
1038:                 'get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L1038_17", 0.0000)',  <-- ERROR
1039:                 'Final penalty-adjusted score'
```

## Error 125
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 1141
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1140:             question_id = data.get('question_id', 'UNKNOWN')
1141:             raw_score = data.get('raw_score', get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L1141_46", 0.0))  <-- ERROR
1142: 
```

## Error 126
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 1161
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1160:             adjusted_score = final_posterior * (1 - validation_penalty)
1161:             adjusted_score = max(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L1161_33", 0.0), min(get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("auto_param_L1161_42", 1.0), adjusted_score))  <-- ERROR
1162: 
```

## Error 127
- **File**: `farfan_core/farfan_core/analysis/bayesian_multilevel_system.py`
- **Line**: 1208
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1207:             peer_comparison = None
1208:             peer_penalty = get_parameter_loader().get("farfan_core.analysis.bayesian_multilevel_system.BayesianPortfolioComposer.__init__").get("peer_penalty", 0.0) # Refactored  <-- ERROR
1209: 
```

## Error 128
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 28
- **Problem**: Syntax error involving get_parameter_loader().
```python
27: from typing import (
28: # from farfan_core import get_parameter_loader  # CALIBRATION DISABLED  <-- ERROR
29: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 129
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 96
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
95:                 lead_time_days=90,
96:                 capacity_constraints={"technical_staff": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L96_57", 0.8), "financial_resources": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L96_85", 0.6)}  <-- ERROR
97:             ),
```

## Error 130
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 107
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
106:                 lead_time_days=120,
107:                 capacity_constraints={"planning_expertise": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L107_60", 0.7), "resources": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L107_78", 0.8)}  <-- ERROR
108:             ),
```

## Error 131
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 118
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
117:                 lead_time_days=365,
118:                 capacity_constraints={"implementation_capacity": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L118_65", 0.65), "coordination": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L118_87", 0.60)}  <-- ERROR
119:             )
```

## Error 132
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 184
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
183:         self.ngram_range = ngram_range if ngram_range is not None else (1, 3)
184:         self.similarity_threshold = similarity_threshold if similarity_threshold is not None else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalOntology.__init__").get("auto_param_L184_98", 0.3)  <-- ERROR
185: 
```

## Error 133
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 261
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
260:         else:
261:             semantic_cube["measures"]["overall_coherence"] = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer.extract_semantic_cube").get("auto_param_L261_61", 0.0)  <-- ERROR
262: 
```

## Error 134
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 281
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
280:                 "coherence_scores": [],
281:                 "semantic_complexity": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._empty_semantic_cube").get("auto_param_L281_39", 0.0)  <-- ERROR
282:             },
```

## Error 135
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 304
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
303:             # Return list of lists if numpy is not available
304:             return [[get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._vectorize_segments").get("auto_param_L304_21", 0.0)] * 100 for _ in range(len(segments))]  <-- ERROR
305: 
```

## Error 136
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 328
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
327:         # Calculate semantic density (simplified)
328:         coherence_score = min(get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._process_segment").get("auto_param_L328_30", 1.0), len(sentences) / 10) if sentences else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._process_segment").get("auto_param_L328_74", 0.0)  <-- ERROR
329: 
```

## Error 137
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 351
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
350:         for link_name, link_obj in self.ontology.value_chain_links.items():
351:             score = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._classify_value_chain_link").get("score", 0.0) # Refactored  <-- ERROR
352:             total_keywords = 0
```

## Error 138
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 364
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
363:                 if keyword.lower().replace("_", " ") in segment_lower:
364:             link_scores[link_name] = score / total_keywords if total_keywords > 0 else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._classify_value_chain_link").get("auto_param_L364_87", 0.0)  <-- ERROR
365: 
```

## Error 139
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 380
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
379:         for domain, keywords in self.ontology.policy_domains.items():
380:             domain_scores[domain] = score / len(keywords) if keywords else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._classify_policy_domain").get("auto_param_L380_75", 0.0)  <-- ERROR
381: 
```

## Error 140
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 396
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
395:         for theme, keywords in self.ontology.cross_cutting_themes.items():
396:             theme_scores[theme] = score / len(keywords) if keywords else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._classify_cross_cutting_themes").get("auto_param_L396_73", 0.0)  <-- ERROR
397: 
```

## Error 141
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 412
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
411:         max_expected_concepts = 20
412:         return min(get_parameter_loader().get("farfan_core.analysis.Analyzer_one.SemanticAnalyzer._calculate_semantic_complexity").get("auto_param_L412_19", 1.0), len(unique_concepts) / max_expected_concepts)  <-- ERROR
413: 
```

## Error 142
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 424
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
423:         if IsolationForest is not None:
424:             self.bottleneck_detector = IsolationForest(contamination=get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer.__init__").get("auto_param_L424_69", 0.1), random_state=RANDOM_SEED)  <-- ERROR
425:         else:
```

## Error 143
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 468
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
467:             return {
468:                 "capacity_utilization": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_throughput_metrics").get("auto_param_L468_40", 0.0)  <-- ERROR
469:             }
```

## Error 144
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 513
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
512:         for constraint_type, constraint_value in link_config.capacity_constraints.items():
513:                     "severity": "high" if constraint_value < get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._detect_bottlenecks").get("auto_param_L513_61", 0.5) else "medium"  <-- ERROR
514:                 }
```

## Error 145
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 518
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
517:         for bottleneck_type in link_config.bottlenecks:
518:             score = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._detect_bottlenecks").get("score", 0.0) # Refactored  <-- ERROR
519:             if segments:
```

## Error 146
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 529
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
528:                 "score": score,
529:                 "severity": "high" if score > get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._detect_bottlenecks").get("auto_param_L529_46", 0.2) else "medium" if score > get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._detect_bottlenecks").get("auto_param_L529_75", 0.1) else "low"  <-- ERROR
530:             }
```

## Error 147
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 539
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
538:         # Throughput loss (quadratic)
539:         target_throughput = 5get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L539_29", 0.0)  <-- ERROR
540:         throughput_gap = max(0, target_throughput - metrics["throughput"])
```

## Error 148
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 544
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
543:         # Efficiency loss (exponential)
544:         target_efficiency = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("target_efficiency", 0.8) # Refactored  <-- ERROR
545:         efficiency_gap = max(0, target_efficiency - metrics["efficiency_score"])
```

## Error 149
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 556
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
555:         capacity_utilization = metrics["capacity_utilization"]
556:         time_multiplier = 1 + (1 - capacity_utilization) * get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L556_59", 0.5)  <-- ERROR
557:         time_loss = baseline_time * (time_multiplier - 1)
```

## Error 150
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 560
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
559:         # Composite loss
560:         composite_loss = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L560_25", 0.4) * throughput_loss + get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L560_49", 0.4) * efficiency_loss + get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._calculate_loss_functions").get("auto_param_L560_73", 0.2) * time_loss  <-- ERROR
561: 
```

## Error 151
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 576
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
575:         for link_name, metrics in performance_analysis["value_chain_metrics"].items():
576:             if metrics["efficiency_score"] < get_parameter_loader().get("farfan_core.analysis.Analyzer_one.PerformanceAnalyzer._generate_recommendations").get("auto_param_L576_45", 0.5):  <-- ERROR
577:                 recommendations.append({
```

## Error 152
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 666
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
665:         for link_name, metrics in performance_analysis["value_chain_metrics"].items():
666:                 criticality_score += get_parameter_loader().get("farfan_core.analysis.Analyzer_one.TextMiningEngine._identify_critical_links").get("auto_param_L666_37", 0.4)  <-- ERROR
667: 
```

## Error 153
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 670
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
669:             if metrics["throughput"] < 20:
670:                 criticality_score += get_parameter_loader().get("farfan_core.analysis.Analyzer_one.TextMiningEngine._identify_critical_links").get("auto_param_L670_37", 0.3)  <-- ERROR
671: 
```

## Error 154
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 678
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
677:                 loss = performance_analysis["operational_loss_functions"][link_name]["composite_loss"]
678:             if criticality_score > get_parameter_loader().get("farfan_core.analysis.Analyzer_one.TextMiningEngine._identify_critical_links").get("auto_param_L678_35", 0.4):  <-- ERROR
679:                 critical_links[link_name] = criticality_score
```

## Error 155
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 883
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
882:         else:
883:             avg_efficiency = get_parameter_loader().get("farfan_core.analysis.Analyzer_one.MunicipalAnalyzer._generate_summary").get("avg_efficiency", 0.0) # Refactored  <-- ERROR
884: 
```

## Error 156
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 1127
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1126:             "coverage_ratio": (
1127:                 matched_contracts / total_contracts if total_contracts else get_parameter_loader().get("farfan_core.analysis.Analyzer_one.CanonicalQuestionSegmenter.segment_plan").get("auto_param_L1127_76", 0.0)  <-- ERROR
1128:             ),
```

## Error 157
- **File**: `farfan_core/farfan_core/analysis/Analyzer_one.py`
- **Line**: 1744
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1743:             "analysis": {
1744:                 "efficiency_threshold": get_parameter_loader().get("farfan_core.analysis.Analyzer_one.ConfigurationManager.load_config").get("auto_param_L1744_40", 0.5),  <-- ERROR
1745:                 "throughput_threshold": 20
```

## Error 158
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 41
- **Problem**: Syntax error involving get_parameter_loader().
```python
40: from sklearn.metrics.pairwise import cosine_similarity
41: from farfan_core import get_parameter_loader  <-- ERROR
42: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 159
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 511
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
510:         Args:
511:             prior_strength: Prior belief strength (get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer.__init__").get("auto_param_L510_51", 1.0) = weak, 1get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer.__init__").get("auto_param_L510_64", 0.0) = strong)  <-- ERROR
512:         """
```

## Error 160
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 617
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
616:         obs_mean = np.mean(observations)
617:         obs_std = np.std(observations, ddof=1) if n_obs > 1 else get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer.__init__").get("auto_param_L616_65", 1.0)  <-- ERROR
618: 
```

## Error 161
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 654
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
653:         """
654:         elif credible_interval_width > get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer.__init__").get("auto_param_L653_39", 0.15):  <-- ERROR
655:             return "strong"
```

## Error 162
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 674
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
673:         if len(observations) < 2:
674:             return get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._compute_coherence").get("auto_param_L673_19", 1.0)  <-- ERROR
675: 
```

## Error 163
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 681
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
680:         if mean_val == 0:
681:             return get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._compute_coherence").get("auto_param_L680_19", 0.0)  <-- ERROR
682: 
```

## Error 164
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 688
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
687: 
688:         return float(np.clip(coherence, get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._compute_coherence").get("auto_param_L687_40", 0.0), get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._compute_coherence").get("auto_param_L687_45", 1.0)))  <-- ERROR
689: 
```

## Error 165
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 701
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
700:         """Return null evaluation when no data available."""
701:             posterior_records=[{"coherence": get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L700_45", 0.0)}],  <-- ERROR
702:         )
```

## Error 166
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 737
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
736:         if not policy_a_values or not policy_b_values:
737:             return {"probability_a_better": get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L736_44", 0.5), "bayes_factor": get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L736_65", 1.0)}  <-- ERROR
738: 
```

## Error 167
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 754
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
753:         prob_a_better = float(np.mean(samples_a > samples_b))
754:         if prob_a_better > get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L753_27", 0.5):  <-- ERROR
755:             bayes_factor = prob_a_better / (1 - prob_a_better)
```

## Error 168
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 849
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
848:         top_k: int = 10,
849:         min_score: float = get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L848_27", 0.0),  <-- ERROR
850:     ) -> list[tuple[SemanticChunk, float]]:
```

## Error 169
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 904
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
903:     top_k_rerank: int = 10  # Cross-encoder rerank
904:     prior_strength: float = get_parameter_loader().get("farfan_core.processing.embedding_policy.BayesianNumericalAnalyzer._null_evaluation").get("auto_param_L903_28", 1.0)  # Weakly informative prior  <-- ERROR
905: 
```

## Error 170
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1475
- **Problem**: Concatenated literal (e.g. '1get...'). Missing operator or corrupted default value.
```python
1474:                         if "%" in match.group(0) and value <= 100:
1475:                             value = value / 10get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._extract_numerical_values").get("auto_param_L1474_46", 0.0)  <-- ERROR
1476: 
```

## Error 171
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1510
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1509:         if not relevant_chunks:
1510:             return get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._generate_query_from_pdq").get("auto_param_L1509_19", 0.0)  <-- ERROR
1511: 
```

## Error 172
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1515
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1514:         semantic_confidence = (
1515:             float(np.mean(semantic_scores)) if semantic_scores else get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._generate_query_from_pdq").get("auto_param_L1514_68", 0.0)  <-- ERROR
1516:         )
```

## Error 173
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1523
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1522:         evidence_strength_map = {
1523:             "very_strong": get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._generate_query_from_pdq").get("auto_param_L1522_27", 1.0),  <-- ERROR
1524:         }
```

## Error 174
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1533
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1532:         # Combined confidence: weighted average
1533:         return float(np.clip(overall_confidence, get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._generate_query_from_pdq").get("auto_param_L1532_49", 0.0), get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder._generate_query_from_pdq").get("auto_param_L1532_54", 1.0)))  <-- ERROR
1534: 
```

## Error 175
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1631
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1630: 
1631:     Version: get_parameter_loader().get("farfan_core.processing.embedding_policy.PolicyAnalysisEmbedder.get_diagnostics").get("auto_param_L1630_13", 1.0).0  <-- ERROR
1632:     Producer Type: Embedding / Semantic Search
```

## Error 176
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1745
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1744:         """Extract confidence from P-D-Q report"""
1745:         return report.get("confidence", get_parameter_loader().get("farfan_core.processing.embedding_policy.EmbeddingPolicyProducer.get_pdq_confidence").get("auto_param_L1744_40", 0.0))  <-- ERROR
1746: 
```

## Error 177
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1801
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1800:         """Extract probability that A is better than B"""
1801:         return comparison.get("probability_a_better", get_parameter_loader().get("farfan_core.processing.embedding_policy.EmbeddingPolicyProducer.get_comparison_probability").get("auto_param_L1800_54", 0.5))  <-- ERROR
1802: 
```

## Error 178
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1806
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1805:         """Extract Bayes factor from comparison"""
1806:         return comparison.get("bayes_factor", get_parameter_loader().get("farfan_core.processing.embedding_policy.EmbeddingPolicyProducer.get_comparison_bayes_factor").get("auto_param_L1805_46", 1.0))  <-- ERROR
1807: 
```

## Error 179
- **File**: `farfan_core/farfan_core/processing/embedding_policy.py`
- **Line**: 1811
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1810:         """Extract mean difference from comparison"""
1811:         return comparison.get("difference_mean", get_parameter_loader().get("farfan_core.processing.embedding_policy.EmbeddingPolicyProducer.get_comparison_difference_mean").get("auto_param_L1810_49", 0.0))  <-- ERROR
1812: 
```

## Error 180
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 30
- **Problem**: Syntax error involving get_parameter_loader().
```python
29: from typing import TYPE_CHECKING, Any, TypeVar
30: # from farfan_core import get_parameter_loader  # CALIBRATION DISABLED  <-- ERROR
31: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 181
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 582
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
581:         """
582:         Ensures that a list of weights sums to get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L582_47", 1.0) within a small tolerance.  <-- ERROR
583: 
```

## Error 182
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 604
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
603: 
604:             msg = f"Weight sum validation failed: sum={weight_sum:.6f}, expected=get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L604_81", 1.0)"  <-- ERROR
605:             logger.error(msg)
```

## Error 183
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 665
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
664:         if not scores:
665:             return get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L665_19", 0.0)  <-- ERROR
666: 
```

## Error 184
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 669
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
668:             # Equal weights
669:             weights = [get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L669_23", 1.0) / len(scores)] * len(scores)  <-- ERROR
670: 
```

## Error 185
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 679
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
678: 
679:         # Validate weights sum to get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L679_34", 1.0)  <-- ERROR
680:         valid, msg = self.validate_weights(weights)
```

## Error 186
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 714
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
713:         # Clamp score to valid range [0, 3]
714:         clamped_score = max(get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L714_28", 0.0), min(3.0, score))  <-- ERROR
715: 
```

## Error 187
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 727
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
726:         if thresholds:
727:             acceptable_threshold = get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("acceptable_threshold", 0.55) # Refactored  <-- ERROR
728: 
```

## Error 188
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 795
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
794:                 area_id=area_id,
795:                 score=get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L795_22", 0.0),  <-- ERROR
796:                 quality_level="INSUFICIENTE",
```

## Error 189
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 807
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
806:                 area_id=area_id,
807:                 score=get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L807_22", 0.0),  <-- ERROR
808:                 quality_level="INSUFICIENTE",
```

## Error 190
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 831
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
830:                 area_id=area_id,
831:                 score=get_parameter_loader().get("farfan_core.processing.aggregation.DimensionAggregator.validate_weights").get("auto_param_L831_22", 0.0),  <-- ERROR
832:                 quality_level="INSUFICIENTE",
```

## Error 191
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1148
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1147:             max_expected = d.validation_details.get('score_max', 3.0) if d.validation_details else 3.0
1148:             normalized.append(max(get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1148_34", 0.0), min(max_expected, d.score)) / max_expected)  <-- ERROR
1149: 
```

## Error 192
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1170
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1169:         # Clamp score to valid range [0, 3]
1170:         clamped_score = max(get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1170_28", 0.0), min(3.0, score))  <-- ERROR
1171: 
```

## Error 193
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1183
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1182:         if thresholds:
1183:             acceptable_threshold = get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("acceptable_threshold", 0.55) # Refactored  <-- ERROR
1184: 
```

## Error 194
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1249
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1248:                 area_name=area_name,
1249:                 score=get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1249_22", 0.0),  <-- ERROR
1250:                 quality_level="INSUFICIENTE",
```

## Error 195
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1266
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1265:                 area_name=area_name,
1266:                 score=get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1266_22", 0.0),  <-- ERROR
1267:                 quality_level="INSUFICIENTE",
```

## Error 196
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1378
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1377: 
1378:     PENALTY_WEIGHT = get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("PENALTY_WEIGHT", 0.3) # Refactored  <-- ERROR
1379:     MAX_SCORE = 3.0
```

## Error 197
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1495
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1494:             # Equal weights
1495:             weights = [get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1495_23", 1.0) / len(scores)] * len(scores)  <-- ERROR
1496: 
```

## Error 198
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1510
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1509: 
1510:         if abs(weight_sum - get_parameter_loader().get("farfan_core.processing.aggregation.AreaPolicyAggregator.normalize_scores").get("auto_param_L1510_28", 1.0)) > tolerance:  <-- ERROR
1511:             msg = f"Cluster weight validation failed: sum={weight_sum:.6f}"
```

## Error 199
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1543
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1542:         if len(scores) <= 1:
1543:             return get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1543_19", 1.0)  <-- ERROR
1544: 
```

## Error 200
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1550
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1549:         variance = sum((s - mean) ** 2 for s in scores) / len(scores)
1550:         std_dev = variance ** get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1550_30", 0.5)  <-- ERROR
1551: 
```

## Error 201
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1555
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1554:         max_std = 3.0
1555:         coherence = max(get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1555_24", 0.0), get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1555_29", 1.0) - (std_dev / max_std))  <-- ERROR
1556: 
```

## Error 202
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1602
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1601:                 areas=[],
1602:                 variance=get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1602_25", 0.0),  <-- ERROR
1603:                 weakest_area=None,
```

## Error 203
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1633
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1632:                 areas=expected_areas,
1633:                 variance=get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1633_25", 0.0),  <-- ERROR
1634:                 weakest_area=None,
```

## Error 204
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1648
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1647:                 areas=expected_areas,
1648:                 variance=get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1648_25", 0.0),  <-- ERROR
1649:                 weakest_area=None,
```

## Error 205
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1672
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1671:                 areas=expected_areas,
1672:                 variance=get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1672_25", 0.0),  <-- ERROR
1673:                 weakest_area=None,
```

## Error 206
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1691
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1690:         else:
1691:         penalty_factor = get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1691_25", 1.0) - (normalized_std * self.PENALTY_WEIGHT)  <-- ERROR
1692:         adjusted_score = weighted_score * penalty_factor
```

## Error 207
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1696
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1695:             "value": coherence,
1696:             "interpretation": "high" if coherence > get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1696_52", 0.8) else "medium" if coherence > get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1696_85", 0.6) else "low"  <-- ERROR
1697:         }
```

## Error 208
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1847
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1846:         if len(scores) <= 1:
1847:             return get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1847_19", 1.0)  <-- ERROR
1848: 
```

## Error 209
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1854
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1853:         variance = sum((s - mean) ** 2 for s in scores) / len(scores)
1854:         std_dev = variance ** get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1854_30", 0.5)  <-- ERROR
1855: 
```

## Error 210
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1858
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1857:         max_std = 3.0
1858:         coherence = max(get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1858_24", 0.0), get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1858_29", 1.0) - (std_dev / max_std))  <-- ERROR
1859: 
```

## Error 211
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1907
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1906:             sum(c.coherence for c in cluster_scores) / len(cluster_scores)
1907:             if cluster_scores else get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1907_35", 0.0)  <-- ERROR
1908:         )
```

## Error 212
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1915
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1914:         validated_dims = sum(1 for d in dimension_scores if d.validation_passed)
1915:         alignment = (get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1915_21", 0.6) * cluster_coherence) + (get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1915_49", 0.4) * validation_rate)  <-- ERROR
1916: 
```

## Error 213
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1941
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1940:         # Clamp score to valid range [0, 3]
1941:         clamped_score = max(get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L1941_28", 0.0), min(3.0, score))  <-- ERROR
1942: 
```

## Error 214
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 1954
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
1953:         if thresholds:
1954:             acceptable_threshold = get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("acceptable_threshold", 0.55) # Refactored  <-- ERROR
1955: 
```

## Error 215
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 2001
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2000:             return MacroScore(
2001:                 strategic_alignment=get_parameter_loader().get("farfan_core.processing.aggregation.ClusterAggregator.analyze_coherence").get("auto_param_L2001_36", 0.0),  <-- ERROR
2002:                 cluster_scores=[],
```

## Error 216
- **File**: `farfan_core/farfan_core/processing/aggregation.py`
- **Line**: 2061
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
2060:         if not cluster_scores:
2061:             return get_parameter_loader().get("farfan_core.processing.aggregation.MacroAggregator._calculate_macro_score").get("auto_param_L2061_19", 0.0)  <-- ERROR
2062:         if not weights:
```

## Error 217
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 32
- **Problem**: Syntax error involving get_parameter_loader().
```python
31: from farfan_core.processing.cpp_ingestion.models import (
32: # from farfan_core import get_parameter_loader  # CALIBRATION DISABLED  <-- ERROR
33: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 218
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 234
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
233:         confidence = Confidence(
234:             ocr=smart_chunk.confidence_metrics.get('extraction_confidence', get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._convert_smart_chunk_to_chunk").get("auto_param_L233_76", 0.95)),  <-- ERROR
235:             typing=smart_chunk.coherence_score
```

## Error 219
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 374
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
373:                     entity_type=pe.entity_type if hasattr(pe, 'entity_type') else 'unknown',
374:                     confidence=pe.confidence if hasattr(pe, 'confidence') else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_entities").get("auto_param_L373_79", 0.8)  <-- ERROR
375:                 )
```

## Error 220
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 533
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
532:         )
533:         avg_completeness = sum(sc.completeness_index for sc in smart_chunks) / len(smart_chunks) if smart_chunks else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L532_118", 0.0)  <-- ERROR
534: 
```

## Error 221
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 537
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
536:         chunks_with_budget = sum(1 for c in chunk_graph.chunks.values() if c.budget)
537:         budget_consistency = chunks_with_budget / len(chunk_graph.chunks) if chunk_graph.chunks else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L536_101", 0.0)  <-- ERROR
538: 
```

## Error 222
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 541
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
540:         chunks_with_time = sum(1 for c in chunk_graph.chunks.values() if c.time_facets.years)
541:         temporal_robustness = chunks_with_time / len(chunk_graph.chunks) if chunk_graph.chunks else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L540_100", 0.0)  <-- ERROR
542: 
```

## Error 223
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 545
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
544:         chunks_with_edges = len({e[0] for e in chunk_graph.edges} | {e[1] for e in chunk_graph.edges})
545:         chunk_context_coverage = chunks_with_edges / len(chunk_graph.chunks) if chunk_graph.chunks else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L544_104", 0.0)  <-- ERROR
546: 
```

## Error 224
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 551
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
550:             boundary_f1=avg_completeness,
551:             kpi_linkage_rate=get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L550_29", 0.0),  # Would need KPI analysis  <-- ERROR
552:             budget_consistency_score=budget_consistency,
```

## Error 225
- **File**: `farfan_core/farfan_core/processing/converter.py`
- **Line**: 652
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
651:                         'dimension': ce.dimension if hasattr(ce, 'dimension') else 'unknown',
652:                         'confidence': ce.confidence if hasattr(ce, 'confidence') else get_parameter_loader().get("farfan_core.processing.spc_ingestion.converter.SmartChunkConverter._extract_kpi").get("auto_param_L651_86", 0.0),  <-- ERROR
653:                     }
```

## Error 226
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 37
- **Problem**: Syntax error involving get_parameter_loader().
```python
36: import numpy as np
37: from farfan_core import get_parameter_loader  <-- ERROR
38: from farfan_core.core.calibration.decorators import calibrated_method
```

## Error 227
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 85
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
84:         if not self.success:
85:             return get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L85_19", 0.0)  <-- ERROR
86: 
```

## Error 228
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 97
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
96:         # Cost efficiency reward (cheaper is better, normalized to 0-1)
97:         typical_cost = get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("typical_cost", 0.01) # Refactored  <-- ERROR
98:         cost_reward = max(0, 1 - (self.cost_usd / (2 * typical_cost)))
```

## Error 229
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 107
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
106:         reward = (
107:         return min(get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L107_19", 1.0), max(get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L107_28", 0.0), reward))  <-- ERROR
108: 
```

## Error 230
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 122
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
121:     # Bayesian posterior (Beta distribution for Thompson Sampling)
122:     beta: float = get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L122_18", 1.0)   # Failures + 1  <-- ERROR
123: 
```

## Error 231
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 126
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
125:     pulls: int = 0
126:     total_reward: float = get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L126_26", 0.0)  <-- ERROR
127:     successes: int = 0
```

## Error 232
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 133
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
132:     # Performance tracking
133:     total_cost_usd: float = get_parameter_loader().get("farfan_core.optimization.rl_strategy.ExecutorMetrics.reward").get("auto_param_L133_28", 0.0)  <-- ERROR
134: 
```

## Error 233
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 143
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
142:         """Calculate mean reward."""
143:         return self.total_reward / self.pulls if self.pulls > 0 else get_parameter_loader().get("farfan_core.optimization.rl_strategy.BanditArm.mean_reward").get("auto_param_L143_69", 0.0)  <-- ERROR
144: 
```

## Error 234
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 150
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
149:         total = self.successes + self.failures
150:         return self.successes / total if total > 0 else get_parameter_loader().get("farfan_core.optimization.rl_strategy.BanditArm.success_rate").get("auto_param_L150_56", 0.0)  <-- ERROR
151: 
```

## Error 235
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 156
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
155:         """Calculate mean duration."""
156:         return self.total_duration_ms / self.pulls if self.pulls > 0 else get_parameter_loader().get("farfan_core.optimization.rl_strategy.BanditArm.mean_duration_ms").get("auto_param_L156_74", 0.0)  <-- ERROR
157: 
```

## Error 236
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 162
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
161:         """Calculate mean cost."""
162:         return self.total_cost_usd / self.pulls if self.pulls > 0 else get_parameter_loader().get("farfan_core.optimization.rl_strategy.BanditArm.mean_cost_usd").get("auto_param_L162_71", 0.0)  <-- ERROR
163: 
```

## Error 237
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 178
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
177:         # Update Bayesian posterior
178:         if metrics.success and reward > get_parameter_loader().get("farfan_core.optimization.rl_strategy.BanditArm.update").get("auto_param_L178_40", 0.5):  <-- ERROR
179:             self.alpha += 1
```

## Error 238
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 367
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
366:         if self.decay:
367:             self.epsilon = self.initial_epsilon / (1 + get_parameter_loader().get("farfan_core.optimization.rl_strategy.EpsilonGreedyAlgorithm.select_arm").get("auto_param_L367_55", 0.001) * self.total_selections)  <-- ERROR
368: 
```

## Error 239
- **File**: `farfan_core/farfan_core/optimization/rl_strategy.py`
- **Line**: 437
- **Problem**: Nested .get() call. The first .get() returns a scalar (float/int), causing AttributeError on the second .get().
```python
436:         elif strategy == OptimizationStrategy.EPSILON_GREEDY:
437:             return EpsilonGreedyAlgorithm(epsilon=get_parameter_loader().get("farfan_core.optimization.rl_strategy.RLStrategyOptimizer._create_algorithm").get("auto_param_L437_50", 0.1), decay=True)  <-- ERROR
438:         else:
```

