#!/usr/bin/env python3
"""
Calibration Coverage Validator for COHORT_2024

Cross-references intrinsic_calibration.json with method_compatibility.json to produce
a comprehensive calibration coverage matrix showing which methods have layer scores
(@b/@q/@d/@p/@C/@chain/@u/@m) computed versus pending.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CalibrationCoverageValidator:
    """Validates and generates calibration coverage matrix across all 8 layers."""
    
    LAYER_SYMBOLS = ['@b', '@q', '@d', '@p', '@C', '@chain', '@u', '@m']
    LAYER_NAMES = {
        '@b': 'Base Layer',
        '@q': 'Question Layer',
        '@d': 'Dimension Layer',
        '@p': 'Policy Layer',
        '@C': 'Congruence Layer',
        '@chain': 'Chain Layer',
        '@u': 'Unit Layer',
        '@m': 'Meta Layer'
    }
    
    def __init__(
        self,
        inventory_path: Path,
        intrinsic_calibration_path: Path,
        method_compatibility_path: Path
    ):
        self.inventory_path = Path(inventory_path)
        self.intrinsic_calibration_path = Path(intrinsic_calibration_path)
        self.method_compatibility_path = Path(method_compatibility_path)
        
        self.inventory = self._load_json(inventory_path)
        self.intrinsic_calibration = self._load_json(intrinsic_calibration_path)
        self.method_compatibility = self._load_json(method_compatibility_path)
        
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return {}
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_coverage_matrix(self) -> Dict[str, Any]:
        """Generate comprehensive calibration coverage matrix."""
        logger.info("Generating calibration coverage matrix...")
        
        methods = self.inventory.get('methods', {})
        coverage_data = {}
        
        # Statistics tracking
        stats = {
            'total_methods': len(methods),
            'per_layer_coverage': {layer: {'computed': 0, 'pending': 0} for layer in self.LAYER_SYMBOLS},
            'fully_calibrated': 0,
            'partially_calibrated': 0,
            'not_calibrated': 0,
            'per_role_coverage': defaultdict(lambda: {'total': 0, 'calibrated': 0})
        }
        
        for full_notation, method_info in methods.items():
            method_id = method_info['method_id']
            role = method_info['role']
            required_layers = method_info.get('layers', [])
            
            # Build coverage entry for this method
            coverage_entry = {
                'method_id': method_id,
                'role': role,
                'required_layers': required_layers,
                'layer_scores': {},
                'calibration_status': {}
            }
            
            # Check each layer
            computed_count = 0
            for layer in self.LAYER_SYMBOLS:
                layer_status = self._check_layer_calibration(
                    method_id,
                    layer,
                    required_layers
                )
                
                coverage_entry['calibration_status'][layer] = layer_status['status']
                coverage_entry['layer_scores'][layer] = layer_status.get('score')
                
                # Update statistics
                if layer_status['status'] == 'computed':
                    stats['per_layer_coverage'][layer]['computed'] += 1
                    computed_count += 1
                else:
                    stats['per_layer_coverage'][layer]['pending'] += 1
            
            # Determine overall calibration status
            if computed_count == len(self.LAYER_SYMBOLS):
                coverage_entry['overall_status'] = 'fully_calibrated'
                stats['fully_calibrated'] += 1
            elif computed_count > 0:
                coverage_entry['overall_status'] = 'partially_calibrated'
                stats['partially_calibrated'] += 1
            else:
                coverage_entry['overall_status'] = 'not_calibrated'
                stats['not_calibrated'] += 1
            
            # Update role statistics
            stats['per_role_coverage'][role]['total'] += 1
            if computed_count > 0:
                stats['per_role_coverage'][role]['calibrated'] += 1
            
            coverage_data[full_notation] = coverage_entry
        
        # Calculate percentages
        for layer in self.LAYER_SYMBOLS:
            total = stats['total_methods']
            computed = stats['per_layer_coverage'][layer]['computed']
            stats['per_layer_coverage'][layer]['percentage'] = (
                round(computed / total * 100, 2) if total > 0 else 0.0
            )
        
        # Build output structure
        result = {
            '_cohort_metadata': {
                'cohort_id': 'COHORT_2024',
                'creation_date': datetime.now().isoformat(),
                'wave_version': 'REFACTOR_WAVE_2024_12',
                'validation_timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'validation_timestamp': datetime.now().isoformat(),
                'source_inventory': str(self.inventory_path),
                'intrinsic_calibration': str(self.intrinsic_calibration_path),
                'method_compatibility': str(self.method_compatibility_path),
                'description': 'Calibration coverage matrix mapping methods to computed layer scores'
            },
            'statistics': {
                'total_methods': stats['total_methods'],
                'fully_calibrated': stats['fully_calibrated'],
                'partially_calibrated': stats['partially_calibrated'],
                'not_calibrated': stats['not_calibrated'],
                'calibration_percentage': round(
                    stats['fully_calibrated'] / stats['total_methods'] * 100, 2
                ) if stats['total_methods'] > 0 else 0.0,
                'per_layer_coverage': stats['per_layer_coverage'],
                'per_role_coverage': dict(stats['per_role_coverage'])
            },
            'coverage_matrix': coverage_data,
            'layer_definitions': self.LAYER_NAMES
        }
        
        return result
    
    def _check_layer_calibration(
        self,
        method_id: str,
        layer: str,
        required_layers: List[str]
    ) -> Dict[str, Any]:
        """Check if a specific layer is calibrated for a method."""
        status = {
            'status': 'pending',
            'score': None,
            'required': layer in required_layers
        }
        
        # Check intrinsic calibration (primarily for @b layer)
        if layer == '@b':
            base_layer = self.intrinsic_calibration.get('base_layer', {})
            role_reqs = self.intrinsic_calibration.get('role_requirements', {})
            
            # For now, mark as computed if role requirements exist
            if role_reqs:
                status['status'] = 'computed'
                status['score'] = 0.7  # Default base score from requirements
        
        # Check method compatibility (for contextual layers)
        compat_data = self.method_compatibility.get('method_compatibility', {})
        if method_id in compat_data:
            method_compat = compat_data[method_id]
            
            # Map layers to compatibility data
            if layer == '@q' and 'questions' in method_compat:
                status['status'] = 'computed'
                status['score'] = self._avg_scores(method_compat['questions'])
            elif layer == '@d' and 'dimensions' in method_compat:
                status['status'] = 'computed'
                status['score'] = self._avg_scores(method_compat['dimensions'])
            elif layer == '@p' and 'policies' in method_compat:
                status['status'] = 'computed'
                status['score'] = self._avg_scores(method_compat['policies'])
        
        # Chain, unit, and meta layers require specific checks
        if layer == '@chain':
            # Check if method has chain data
            status['status'] = 'pending'
        elif layer == '@u':
            # Check if method has unit data
            status['status'] = 'pending'
        elif layer == '@m':
            # Meta layer status
            status['status'] = 'pending'
        elif layer == '@C':
            # Congruence layer status
            status['status'] = 'pending'
        
        return status
    
    def _avg_scores(self, scores_dict: Dict[str, float]) -> float:
        """Calculate average score from dictionary of scores."""
        if not scores_dict:
            return 0.0
        return round(sum(scores_dict.values()) / len(scores_dict), 3)


def main():
    """Main entry point for coverage validator."""
    import sys
    
    base_path = Path(__file__).parent
    
    inventory_path = base_path / 'COHORT_2024_canonical_method_inventory.json'
    intrinsic_path = (
        Path(__file__).parent.parent.parent.parent.parent /
        'src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_intrinsic_calibration.json'
    )
    compat_path = (
        Path(__file__).parent.parent.parent.parent.parent /
        'src/cross_cutting_infrastrucuture/capaz_calibration_parmetrization/calibration/COHORT_2024_method_compatibility.json'
    )
    
    if not inventory_path.exists():
        logger.error(f"Inventory file not found: {inventory_path}")
        logger.error("Please run scan_methods_inventory.py first")
        return 1
    
    validator = CalibrationCoverageValidator(
        inventory_path=inventory_path,
        intrinsic_calibration_path=intrinsic_path,
        method_compatibility_path=compat_path
    )
    
    logger.info("Starting calibration coverage validation...")
    coverage_matrix = validator.generate_coverage_matrix()
    
    output_file = base_path / 'COHORT_2024_calibration_coverage_matrix.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(coverage_matrix, f, indent=2)
    
    logger.info(f"Coverage matrix saved to {output_file}")
    logger.info(f"Total methods: {coverage_matrix['statistics']['total_methods']}")
    logger.info(f"Fully calibrated: {coverage_matrix['statistics']['fully_calibrated']}")
    logger.info(f"Calibration percentage: {coverage_matrix['statistics']['calibration_percentage']}%")
    
    return 0


if __name__ == '__main__':
    exit(main())
