#!/usr/bin/env python3
"""Compara outputs de v4 y v5 para entender diferencias."""

import json
from collections import Counter

v4 = json.load(open('METHODS_DISPENSARY_SIGNATURES_ENRICHED_EPISTEMOLOGY.json'))
v5 = json.load(open('METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json'))

print('='*80)
print('QUALITY METRICS COMPARISON')
print('='*80)
print('\nV4 Quality Metrics:')
for k, v in v4['quality_metrics'].items():
    print(f'  {k}: {v}')

print('\nV5 Quality Metrics:')
for k, v in v5['quality_metrics'].items():
    print(f'  {k}: {v}')

# Analizar diferencias a nivel de método
print('\n' + '='*80)
print('METHOD LEVEL ANALYSIS')
print('='*80)

v4_method_levels = []
v5_method_levels = []

for class_name in v4.keys():
    if class_name == 'quality_metrics':
        continue
    for method_name, method in v4[class_name].get('methods', {}).items():
        ec = method.get('epistemological_classification', {})
        level = ec.get('level', 'UNKNOWN')
        v4_method_levels.append(level)

for class_name in v5.keys():
    if class_name in ['quality_metrics', '_pipeline_metadata']:
        continue
    for method_name, method in v5[class_name].get('methods', {}).items():
        ec = method.get('epistemological_classification', {})
        level = ec.get('level', 'UNKNOWN')
        v5_method_levels.append(level)

print(f'\nV4 Method Level Distribution:')
for level, count in sorted(Counter(v4_method_levels).items()):
    print(f'  {level}: {count}')

print(f'\nV5 Method Level Distribution:')
for level, count in sorted(Counter(v5_method_levels).items()):
    print(f'  {level}: {count}')

# Encontrar métodos con diferente clasificación
print('\n' + '='*80)
print('METHODS WITH DIFFERENT CLASSIFICATIONS (first 20)')
print('='*80)

count = 0
for class_name in v4.keys():
    if class_name == 'quality_metrics':
        continue
    if class_name not in v5 or class_name == '_pipeline_metadata':
        continue

    for method_name, method_v4 in v4[class_name].get('methods', {}).items():
        method_v5 = v5[class_name].get('methods', {}).get(method_name)
        if not method_v5:
            continue

        level_v4 = method_v4.get('epistemological_classification', {}).get('level')
        level_v5 = method_v5.get('epistemological_classification', {}).get('level')

        if level_v4 != level_v5:
            count += 1
            if count <= 20:
                print(f'{class_name}.{method_name}:')
                print(f'  v4: {level_v4}')
                print(f'  v5: {level_v5}')

                # Mostrar evidencia de decisión
                ev_v4 = method_v4.get('epistemological_classification', {}).get('classification_evidence', {})
                ev_v5 = method_v5.get('epistemological_classification', {}).get('classification_evidence', {})

                if 'decision_path' in ev_v4:
                    print(f'  v4 path: {ev_v4.get("decision_path", "N/A")}')
                if 'selected_rule_id' in ev_v5:
                    print(f'  v5 rule: {ev_v5.get("selected_rule_id", "N/A")}')
                print()

print(f'\nTotal methods with different classification: {count}')
