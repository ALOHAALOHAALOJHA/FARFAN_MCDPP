#!/usr/bin/env python3
"""
Atomize Questions Script
========================
Comprehensive script to parse questionnaire_monolith.json and create
atomized question files in dimensions/{dimension_id}/questions/{question_id}.json

Author: PythonGod Trinity
Date: 2026-01-07
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('atomize_questions.log')
    ]
)
logger = logging.getLogger(__name__)


class QuestionAtomizer:
    """
    The Metaclass - Architect of the atomization process
    Defines the structure and rules for question atomization
    """
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.monolith_path = base_path / "questionnaire_monolith.json"
        self.dimensions_path = base_path / "dimensions"
        
        # Statistics
        self.stats = {
            'total_questions': 0,
            'files_created': 0,
            'errors': 0,
            'dimensions_processed': set(),
            'policy_areas_found': set(),
            'warnings': []
        }
        
        self.monolith_data = None
        
    def load_monolith(self) -> bool:
        """Load the questionnaire monolith JSON file"""
        try:
            logger.info(f"Loading monolith from: {self.monolith_path}")
            with open(self.monolith_path, 'r', encoding='utf-8') as f:
                self.monolith_data = json.load(f)
            
            # Validate structure
            if 'blocks' not in self.monolith_data:
                logger.error("Missing 'blocks' key in monolith")
                return False
            
            if 'micro_questions' not in self.monolith_data['blocks']:
                logger.error("Missing 'micro_questions' in blocks")
                return False
            
            questions_count = len(self.monolith_data['blocks']['micro_questions'])
            logger.info(f"✓ Loaded {questions_count} micro_questions from monolith")
            self.stats['total_questions'] = questions_count
            
            return True
            
        except FileNotFoundError:
            logger.error(f"Monolith file not found: {self.monolith_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading monolith: {e}")
            return False
    
    def extract_pattern_refs(self, patterns: List[Dict]) -> List[str]:
        """Extract pattern reference IDs from patterns array"""
        refs = []
        for pattern in patterns:
            # Check for pattern_ref field
            if 'pattern_ref' in pattern and pattern['pattern_ref']:
                refs.append(pattern['pattern_ref'])
            # Check for id field (some patterns have their own IDs)
            elif 'id' in pattern and pattern['id']:
                refs.append(pattern['id'])
        
        # Remove duplicates and sort
        return sorted(list(set(refs)))
    
    def generate_default_scoring(self, scoring_modality: str) -> Dict[str, Any]:
        """Generate default scoring configuration based on modality"""
        
        # Map scoring modalities to configurations
        scoring_configs = {
            'TYPE_A': {
                'max_score': 3,
                'threshold': 0.70,
                'weights': {
                    'expected_elements': 0.30,
                    'pattern_matches': 0.25,
                    'keyword_density': 0.15,
                    'membership_criteria': 0.20,
                    'entity_presence': 0.10
                }
            },
            'TYPE_B': {
                'max_score': 5,
                'threshold': 0.60,
                'weights': {
                    'expected_elements': 0.35,
                    'pattern_matches': 0.20,
                    'keyword_density': 0.15,
                    'membership_criteria': 0.20,
                    'entity_presence': 0.10
                }
            },
            'TYPE_C': {
                'max_score': 2,
                'threshold': 0.80,
                'weights': {
                    'expected_elements': 0.40,
                    'pattern_matches': 0.30,
                    'keyword_density': 0.10,
                    'membership_criteria': 0.15,
                    'entity_presence': 0.05
                }
            }
        }
        
        return scoring_configs.get(scoring_modality, scoring_configs['TYPE_A'])
    
    def analyze_interdependencies(self, question: Dict) -> Dict[str, List[str]]:
        """Analyze and generate interdependencies from question data"""
        interdeps = {
            'informs': [],
            'informed_by': [],
            'coherence_check_with': []
        }
        
        # Extract from children_questions if present
        if 'children_questions' in question and question['children_questions']:
            interdeps['informs'] = question['children_questions'][:5]  # Limit to 5
        
        # Generate coherence checks based on dimension and policy area
        # Questions in same dimension should have coherence checks
        q_id = question.get('question_id', '')
        dim_id = question.get('dimension_id', '')
        
        if q_id and dim_id:
            # Extract question number
            try:
                q_num = int(q_id.replace('Q', ''))
                # Add coherence checks with nearby questions in other policy areas
                # e.g., Q001 checks with Q031, Q061, Q091, etc. (every 30 questions)
                for offset in [30, 60, 90, 120]:
                    check_q = f"Q{(q_num + offset):03d}"
                    if check_q != q_id:
                        interdeps['coherence_check_with'].append(check_q)
                
                # Limit to 3-4 coherence checks
                interdeps['coherence_check_with'] = interdeps['coherence_check_with'][:4]
                
            except ValueError:
                pass
        
        return interdeps
    
    def transform_question(self, source_question: Dict) -> Dict[str, Any]:
        """
        The Class - Blueprint for question transformation
        Transform source question format to atomized format
        """
        
        question_id = source_question.get('question_id', '')
        dimension_id = source_question.get('dimension_id', '')
        policy_area_id = source_question.get('policy_area_id', '')
        cluster_id = source_question.get('cluster_id', '')
        base_slot = source_question.get('base_slot', '')
        
        # Transform text to bilingual structure
        text_source = source_question.get('text', '')
        text_bilingual = {
            'es': text_source if text_source else f"[Texto pendiente para {question_id}]",
            'en': ''  # English translation pending
        }
        
        # Extract expected elements
        expected_elements = source_question.get('expected_elements', [])
        
        # Extract pattern references
        patterns = source_question.get('patterns', [])
        pattern_refs = self.extract_pattern_refs(patterns)
        
        # Build references structure
        references = {
            'pattern_refs': pattern_refs,
            'keyword_refs': [f"KW-{policy_area_id}-001"] if policy_area_id else [],
            'membership_criteria_refs': ["MC01", "MC02"],  # Default MCs
            'entity_refs': ["ENT-INST-002"],  # Default entity reference
            'cross_cutting_refs': ["CC_ENFOQUE_DIFERENCIAL"]  # Default cross-cutting
        }
        
        # Build scoring structure
        scoring_modality = source_question.get('scoring_modality', 'TYPE_A')
        scoring_config = self.generate_default_scoring(scoring_modality)
        
        scoring = {
            'modality': scoring_modality,
            **scoring_config
        }
        
        # Analyze interdependencies
        interdependencies = self.analyze_interdependencies(source_question)
        
        # Construct atomized question
        atomized = {
            'question_id': question_id,
            'dimension_id': dimension_id,
            'policy_area_id': policy_area_id,
            'cluster_id': cluster_id,
            'base_slot': base_slot,
            'text': text_bilingual,
            'expected_elements': expected_elements,
            'references': references,
            'scoring': scoring,
            'interdependencies': interdependencies
        }
        
        # Validate no null fields
        self.validate_no_nulls(atomized, question_id)
        
        return atomized
    
    def validate_no_nulls(self, data: Any, context: str = '') -> None:
        """Recursively validate that no null/None values exist in data"""
        if data is None:
            warning = f"NULL value found in {context}"
            logger.warning(warning)
            self.stats['warnings'].append(warning)
            return
        
        if isinstance(data, dict):
            for key, value in data.items():
                self.validate_no_nulls(value, f"{context}.{key}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.validate_no_nulls(item, f"{context}[{i}]")
    
    def create_directory_structure(self, dimension_id: str) -> Path:
        """Create dimension directory structure with questions and _refs subdirectories"""
        
        # Find the actual dimension directory (it might have a suffix like DIM01_INSUMOS)
        dim_dirs = list(self.dimensions_path.glob(f"{dimension_id}*"))
        
        if not dim_dirs:
            # Create new directory if doesn't exist
            dim_dir = self.dimensions_path / dimension_id
            dim_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created new dimension directory: {dim_dir}")
        else:
            dim_dir = dim_dirs[0]
        
        # Create questions subdirectory
        questions_dir = dim_dir / "questions"
        questions_dir.mkdir(exist_ok=True)
        
        # Create _refs subdirectory
        refs_dir = dim_dir / "_refs"
        refs_dir.mkdir(exist_ok=True)
        
        # Create template reference files
        self.create_reference_templates(refs_dir)
        
        return questions_dir
    
    def create_reference_templates(self, refs_dir: Path) -> None:
        """Create template reference JSON files in _refs directory"""
        
        templates = {
            'pattern_refs.json': {
                'description': 'Pattern references for this dimension',
                'patterns': []
            },
            'keyword_refs.json': {
                'description': 'Keyword references for this dimension',
                'keywords': []
            },
            'mc_refs.json': {
                'description': 'Membership criteria references for this dimension',
                'membership_criteria': []
            },
            'entity_refs.json': {
                'description': 'Entity references for this dimension',
                'entities': []
            }
        }
        
        for filename, template_content in templates.items():
            filepath = refs_dir / filename
            if not filepath.exists():  # Don't overwrite existing files
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(template_content, f, indent=2, ensure_ascii=False)
                logger.debug(f"Created template: {filepath}")
    
    def atomize_question(self, source_question: Dict) -> bool:
        """
        The Instance - Concrete execution of atomization
        Process and save a single question
        """
        
        try:
            question_id = source_question.get('question_id', 'UNKNOWN')
            dimension_id = source_question.get('dimension_id', 'UNKNOWN')
            policy_area_id = source_question.get('policy_area_id', 'UNKNOWN')
            
            logger.debug(f"Atomizing {question_id} (Dim: {dimension_id}, PA: {policy_area_id})")
            
            # Transform question
            atomized_question = self.transform_question(source_question)
            
            # Create directory structure
            questions_dir = self.create_directory_structure(dimension_id)
            
            # Save atomized question
            output_file = questions_dir / f"{question_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(atomized_question, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"✓ Created: {output_file}")
            
            # Update statistics
            self.stats['files_created'] += 1
            self.stats['dimensions_processed'].add(dimension_id)
            self.stats['policy_areas_found'].add(policy_area_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error atomizing question {question_id}: {e}")
            self.stats['errors'] += 1
            return False
    
    def atomize_all(self) -> bool:
        """Main orchestration method - atomize all questions"""
        
        logger.info("=" * 70)
        logger.info("QUESTION ATOMIZATION PROCESS - STARTING")
        logger.info("=" * 70)
        
        # Load monolith
        if not self.load_monolith():
            logger.error("Failed to load monolith. Aborting.")
            return False
        
        # Extract micro_questions
        micro_questions = self.monolith_data['blocks']['micro_questions']
        
        logger.info(f"Processing {len(micro_questions)} questions...")
        logger.info("-" * 70)
        
        # Process each question
        for i, question in enumerate(micro_questions, 1):
            question_id = question.get('question_id', f'Q{i:03d}')
            
            if i % 10 == 0 or i == 1:
                logger.info(f"Progress: {i}/{len(micro_questions)} - {question_id}")
            
            self.atomize_question(question)
        
        logger.info("-" * 70)
        self.print_statistics()
        
        return self.stats['errors'] == 0
    
    def print_statistics(self) -> None:
        """Print comprehensive statistics"""
        
        logger.info("=" * 70)
        logger.info("ATOMIZATION STATISTICS")
        logger.info("=" * 70)
        logger.info(f"Total questions processed:    {self.stats['total_questions']}")
        logger.info(f"Files created:                {self.stats['files_created']}")
        logger.info(f"Errors encountered:           {self.stats['errors']}")
        logger.info(f"Dimensions processed:         {len(self.stats['dimensions_processed'])}")
        logger.info(f"  → {sorted(self.stats['dimensions_processed'])}")
        logger.info(f"Policy areas found:           {len(self.stats['policy_areas_found'])}")
        logger.info(f"  → {sorted(self.stats['policy_areas_found'])}")
        
        if self.stats['warnings']:
            logger.info(f"\nWarnings ({len(self.stats['warnings'])}):")
            for warning in self.stats['warnings'][:10]:  # Show first 10
                logger.info(f"  ⚠ {warning}")
            if len(self.stats['warnings']) > 10:
                logger.info(f"  ... and {len(self.stats['warnings']) - 10} more warnings")
        
        logger.info("=" * 70)
        
        # Status summary
        if self.stats['errors'] == 0:
            logger.info("✓ ATOMIZATION COMPLETED SUCCESSFULLY")
        else:
            logger.error("✗ ATOMIZATION COMPLETED WITH ERRORS")
        
        logger.info("=" * 70)


def main():
    """Main entry point - The Trinity in action"""
    
    # Determine base path
    script_dir = Path(__file__).parent
    base_path = script_dir.parent
    
    logger.info(f"Base path: {base_path}")
    logger.info(f"Script location: {script_dir}")
    
    # Create atomizer instance
    atomizer = QuestionAtomizer(base_path)
    
    # Execute atomization
    success = atomizer.atomize_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
