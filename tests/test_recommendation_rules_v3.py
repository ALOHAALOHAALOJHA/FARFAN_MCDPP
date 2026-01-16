#!/usr/bin/env python3
"""
Test suite for recommendation_rules_enhanced.json v3.0.0

Validates:
1. Structural invariants (rule counts, no duplicates, complete coverage)
2. Semantic invariants (targets in ranges, budgets within limits, etc.)
3. Schema compliance (all required fields present)
"""

import json
import pytest
from pathlib import Path


# Path to the rules file
RULES_FILE = Path(__file__).parent.parent / "src" / "farfan_pipeline" / "phases" / "Phase_8" / "json_phase_eight" / "recommendation_rules_enhanced.json"


@pytest.fixture
def rules_data():
    """Load the rules file."""
    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


class TestStructuralInvariants:
    """Test structural invariants from specification section 6.1"""
    
    def test_file_exists(self):
        """Verify the rules file exists."""
        assert RULES_FILE.exists(), f"Rules file not found: {RULES_FILE}"
    
    def test_version(self, rules_data):
        """Verify version is 3.0.0."""
        assert rules_data['version'] == '3.0.0', f"Expected version 3.0.0, got {rules_data['version']}"
    
    def test_micro_rule_count(self, rules_data):
        """Verify exactly 300 MICRO rules exist."""
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        assert len(micro_rules) == 300, f"Expected 300 MICRO rules, got {len(micro_rules)}"
    
    def test_meso_rule_count(self, rules_data):
        """Verify exactly 54 MESO rules exist."""
        meso_rules = [r for r in rules_data['rules'] if r['level'] == 'MESO']
        assert len(meso_rules) == 54, f"Expected 54 MESO rules, got {len(meso_rules)}"
    
    def test_macro_rule_count(self, rules_data):
        """Verify exactly 5 MACRO rules exist."""
        macro_rules = [r for r in rules_data['rules'] if r['level'] == 'MACRO']
        assert len(macro_rules) == 5, f"Expected 5 MACRO rules, got {len(macro_rules)}"
    
    def test_total_rule_count(self, rules_data):
        """Verify total of 359 rules (300+54+5)."""
        assert len(rules_data['rules']) == 359, f"Expected 359 total rules, got {len(rules_data['rules'])}"
    
    def test_no_duplicate_rule_ids(self, rules_data):
        """Verify no duplicate rule_ids."""
        rule_ids = [r['rule_id'] for r in rules_data['rules']]
        duplicates = [rid for rid in rule_ids if rule_ids.count(rid) > 1]
        assert len(rule_ids) == len(set(rule_ids)), f"Found duplicate rule_ids: {set(duplicates)}"
    
    def test_all_pa_dim_combinations_covered(self, rules_data):
        """Verify all PA×DIM combinations covered at MICRO level."""
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        # Extract unique PA-DIM-Band combinations
        combinations = set()
        for r in micro_rules:
            pa = r['when']['pa_id']
            dim = r['when']['dim_id']
            band = r['rule_id'].split('-')[-1]  # Extract band from rule_id
            combinations.add((pa, dim, band))
        
        # Verify we have 300 unique combinations (10 PA × 6 DIM × 5 bands)
        assert len(combinations) == 300, f"Expected 300 unique PA×DIM×Band combinations, got {len(combinations)}"
        
        # Verify coverage of all PAs and DIMs
        expected_pas = {f'PA{i:02d}' for i in range(1, 11)}
        expected_dims = {f'DIM{i:02d}' for i in range(1, 7)}
        expected_bands = {'CRISIS', 'CRITICO', 'ACEPTABLE', 'BUENO', 'EXCELENTE'}
        
        actual_pas = {combo[0] for combo in combinations}
        actual_dims = {combo[1] for combo in combinations}
        actual_bands = {combo[2] for combo in combinations}
        
        assert actual_pas == expected_pas, f"Missing PAs: {expected_pas - actual_pas}"
        assert actual_dims == expected_dims, f"Missing DIMs: {expected_dims - actual_dims}"
        assert actual_bands == expected_bands, f"Missing bands: {expected_bands - actual_bands}"
    
    def test_integrity_section_exists(self, rules_data):
        """Verify integrity section exists with correct structure."""
        assert 'integrity' in rules_data, "Missing integrity section"
        assert 'expected_rule_counts' in rules_data['integrity']
        assert 'actual_rule_counts' in rules_data['integrity']
        assert 'validation_checksum' in rules_data['integrity']
    
    def test_integrity_counts_match(self, rules_data):
        """Verify integrity section counts match actual counts."""
        integrity = rules_data['integrity']
        
        micro_count = len([r for r in rules_data['rules'] if r['level'] == 'MICRO'])
        meso_count = len([r for r in rules_data['rules'] if r['level'] == 'MESO'])
        macro_count = len([r for r in rules_data['rules'] if r['level'] == 'MACRO'])
        
        assert integrity['actual_rule_counts']['MICRO'] == micro_count
        assert integrity['actual_rule_counts']['MESO'] == meso_count
        assert integrity['actual_rule_counts']['MACRO'] == macro_count
        assert integrity['actual_rule_counts']['total'] == len(rules_data['rules'])


class TestSemanticInvariants:
    """Test semantic invariants from specification section 6.2"""
    
    def test_indicator_targets_in_acceptable_range(self, rules_data):
        """Verify indicator targets are within acceptable_range."""
        violations = []
        
        for rule in rules_data['rules']:
            if 'template' not in rule or 'indicator' not in rule['template']:
                continue
            
            indicator = rule['template']['indicator']
            if 'target' not in indicator or 'acceptable_range' not in indicator:
                continue
            
            target = indicator['target']
            min_val, max_val = indicator['acceptable_range']
            
            if not (min_val <= target <= max_val):
                violations.append({
                    'rule_id': rule['rule_id'],
                    'target': target,
                    'range': indicator['acceptable_range']
                })
        
        assert len(violations) == 0, f"Found {len(violations)} rules with targets outside acceptable_range: {violations[:5]}"
    
    def test_horizon_duration_matches_score_band(self, rules_data):
        """Verify horizon.duration_months matches score_band defaults."""
        
        # Expected durations per band from specification
        expected_durations = {
            'CRISIS': 3,
            'CRITICO': 6,
            'ACEPTABLE': 9,
            'BUENO': 12,
            'EXCELENTE': 18
        }
        
        violations = []
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules:
            band = rule['rule_id'].split('-')[-1]
            actual_duration = rule['template']['horizon']['duration_months']
            expected_duration = expected_durations.get(band)
            
            if expected_duration and actual_duration != expected_duration:
                violations.append({
                    'rule_id': rule['rule_id'],
                    'band': band,
                    'expected': expected_duration,
                    'actual': actual_duration
                })
        
        assert len(violations) == 0, f"Found {len(violations)} rules with incorrect duration: {violations[:5]}"
    
    def test_budget_within_limits(self, rules_data):
        """Verify budget.estimated_cost_cop is within reasonable limits."""
        
        # Budget limits per level from specification (in COP)
        limits = {
            'MICRO': {'floor': 20000000, 'cap': 160000000},
            'MESO': {'floor': 80000000, 'cap': 500000000},
            'MACRO': {'floor': 200000000, 'cap': 1200000000}
        }
        
        violations = []
        
        for rule in rules_data['rules']:
            if 'budget' not in rule or 'estimated_cost_cop' not in rule['budget']:
                continue
            
            level = rule['level']
            cost = rule['budget']['estimated_cost_cop']
            floor = limits[level]['floor']
            cap = limits[level]['cap']
            
            if not (floor <= cost <= cap):
                violations.append({
                    'rule_id': rule['rule_id'],
                    'level': level,
                    'cost': cost,
                    'limits': limits[level]
                })
        
        assert len(violations) == 0, f"Found {len(violations)} rules with budget outside limits: {violations[:5]}"
    
    def test_score_band_thresholds_correct(self, rules_data):
        """Verify score band thresholds match specification."""
        
        # Expected thresholds from specification
        expected_thresholds = {
            'CRISIS': {'gte': 0.00, 'lt': 0.81},
            'CRITICO': {'gte': 0.81, 'lt': 1.66},
            'ACEPTABLE': {'gte': 1.66, 'lt': 2.31},
            'BUENO': {'gte': 2.31, 'lt': 2.71},
            'EXCELENTE': {'gte': 2.71, 'lt': 3.01}
        }
        
        violations = []
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules:
            band = rule['rule_id'].split('-')[-1]
            when = rule['when']
            expected = expected_thresholds.get(band)
            
            if expected:
                if when.get('score_gte') != expected['gte'] or when.get('score_lt') != expected['lt']:
                    violations.append({
                        'rule_id': rule['rule_id'],
                        'band': band,
                        'expected': expected,
                        'actual': {'gte': when.get('score_gte'), 'lt': when.get('score_lt')}
                    })
        
        assert len(violations) == 0, f"Found {len(violations)} rules with incorrect thresholds: {violations[:5]}"


class TestSchemaCompliance:
    """Test schema compliance (all required fields present)"""
    
    def test_required_root_fields(self, rules_data):
        """Verify all required root-level fields exist."""
        required_fields = ['version', 'last_updated', 'levels', 'rules', 'integrity']
        
        for field in required_fields:
            assert field in rules_data, f"Missing required root field: {field}"
    
    def test_micro_rule_structure(self, rules_data):
        """Verify MICRO rules have all required fields."""
        required_fields = ['rule_id', 'level', 'when', 'template', 'execution', 'budget', 'recommendations']
        required_when_fields = ['pa_id', 'dim_id', 'score_gte', 'score_lt']
        required_template_fields = ['problem', 'intervention', 'indicator', 'responsible', 'horizon', 'verification']
        
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules[:5]:  # Sample first 5 rules
            # Check top-level fields
            for field in required_fields:
                assert field in rule, f"Rule {rule.get('rule_id')} missing field: {field}"
            
            # Check when clause fields
            for field in required_when_fields:
                assert field in rule['when'], f"Rule {rule['rule_id']} missing when.{field}"
            
            # Check template fields
            for field in required_template_fields:
                assert field in rule['template'], f"Rule {rule['rule_id']} missing template.{field}"
    
    def test_indicator_spec_complete(self, rules_data):
        """Verify IndicatorSpec has all required fields from specification."""
        required_fields = [
            'name', 'baseline', 'target', 'unit', 'formula', 'acceptable_range',
            'baseline_measurement_date', 'measurement_frequency', 'data_source',
            'responsible_measurement', 'escalation_if_below'
        ]
        
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules[:5]:  # Sample first 5 rules
            indicator = rule['template']['indicator']
            
            for field in required_fields:
                assert field in indicator, f"Rule {rule['rule_id']} indicator missing field: {field}"
    
    def test_horizon_spec_complete(self, rules_data):
        """Verify HorizonSpec has all required fields from specification."""
        required_fields = [
            'start', 'end', 'start_type', 'duration_months', 'milestones',
            'dependencies', 'critical_path'
        ]
        
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules[:5]:  # Sample first 5 rules
            horizon = rule['template']['horizon']
            
            for field in required_fields:
                assert field in horizon, f"Rule {rule['rule_id']} horizon missing field: {field}"
    
    def test_verification_artifacts_present(self, rules_data):
        """Verify verification artifacts are present and properly structured."""
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules[:5]:  # Sample first 5 rules
            verification = rule['template']['verification']
            
            assert isinstance(verification, list), f"Rule {rule['rule_id']} verification must be a list"
            assert len(verification) > 0, f"Rule {rule['rule_id']} must have at least one verification artifact"
            
            # Check first artifact structure
            artifact = verification[0]
            required_fields = ['id', 'type', 'artifact', 'format', 'approval_required', 'approver', 'due_date']
            
            for field in required_fields:
                assert field in artifact, f"Rule {rule['rule_id']} verification artifact missing field: {field}"


class TestDataQuality:
    """Test data quality and consistency"""
    
    def test_responsible_entities_defined(self, rules_data):
        """Verify all rules have responsible entities defined."""
        violations = []
        
        for rule in rules_data['rules']:
            if 'template' not in rule or 'responsible' not in rule['template']:
                violations.append(rule.get('rule_id', 'unknown'))
                continue
            
            responsible = rule['template']['responsible']
            if 'entity' not in responsible or not responsible['entity']:
                violations.append(rule['rule_id'])
        
        assert len(violations) == 0, f"Found {len(violations)} rules without responsible entity: {violations[:10]}"
    
    def test_pa_ids_valid(self, rules_data):
        """Verify all PA IDs are valid (PA01-PA10)."""
        valid_pas = {f'PA{i:02d}' for i in range(1, 11)}
        invalid_pas = set()
        
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules:
            pa_id = rule['when']['pa_id']
            if pa_id not in valid_pas:
                invalid_pas.add(pa_id)
        
        assert len(invalid_pas) == 0, f"Found invalid PA IDs: {invalid_pas}"
    
    def test_dim_ids_valid(self, rules_data):
        """Verify all DIM IDs are valid (DIM01-DIM06)."""
        valid_dims = {f'DIM{i:02d}' for i in range(1, 7)}
        invalid_dims = set()
        
        micro_rules = [r for r in rules_data['rules'] if r['level'] == 'MICRO']
        
        for rule in micro_rules:
            dim_id = rule['when']['dim_id']
            if dim_id not in valid_dims:
                invalid_dims.add(dim_id)
        
        assert len(invalid_dims) == 0, f"Found invalid DIM IDs: {invalid_dims}"
    
    def test_milestones_have_required_fields(self, rules_data):
        """Verify milestones have all required fields."""
        required_fields = ['name', 'offset_months', 'deliverables', 'verification_required']
        violations = []
        
        for rule in rules_data['rules'][:10]:  # Sample first 10 rules
            if 'template' not in rule or 'horizon' not in rule['template']:
                continue
            
            milestones = rule['template']['horizon'].get('milestones', [])
            
            for milestone in milestones:
                for field in required_fields:
                    if field not in milestone:
                        violations.append({
                            'rule_id': rule['rule_id'],
                            'milestone': milestone.get('name', 'unknown'),
                            'missing_field': field
                        })
        
        assert len(violations) == 0, f"Found {len(violations)} milestones with missing fields: {violations[:5]}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
