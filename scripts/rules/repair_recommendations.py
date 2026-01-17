"""
FARFAN Pipeline - Recommendation Rules Repair Utility
Audits and repairs question ID references in recommendation_rules_enhanced.json
"""

import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

BASE_PATH = Path("/Users/recovered/Downloads/FARFAN_MCDPP")
RULES_PATH = BASE_PATH / "src/farfan_pipeline/phases/Phase_08/json_phase_eight/recommendation_rules_enhanced.json"

def calculate_question_range(pa_code: str, dim_code: str) -> list[str]:
    """
    Calculates the correct question IDs based on Policy Area and Dimension.
    Assumption: 10 PAs, 6 DIMs per PA, 5 Questions per DIM.
    Total 300 Questions.
    """
    try:
        pa_idx = int(pa_code.replace("PA", ""))
        dim_idx = int(dim_code.replace("DIM", ""))
    except ValueError:
        logger.error(f"Invalid codes: {pa_code}, {dim_code}")
        return []

    # Calculate offset
    # PA starts at (pa-1) * 30
    # DIM starts at (dim-1) * 5 within that PA
    start_idx = (pa_idx - 1) * 30 + (dim_idx - 1) * 5 + 1
    
    questions = []
    for i in range(5):
        q_num = start_idx + i
        questions.append(f"Q{q_num:03d}")
    
    return questions

def calculate_checksum(data: dict) -> str:
    """Calculates SHA256 checksum of the JSON content."""
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

def repair_rules():
    if not RULES_PATH.exists():
        logger.error(f"File not found: {RULES_PATH}")
        return

    logger.info(f"Loading rules from {RULES_PATH}")
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rules = data.get("rules", [])
    updates_count = 0
    
    logger.info("Auditing and repairing question references...")

    for rule in rules:
        rule_id = rule.get("rule_id", "")
        # Parse Rule ID structure: REC-MICRO-PAxx-DIMxx-BAND
        parts = rule_id.split("-")
        
        if len(parts) >= 5 and parts[1] == "MICRO":
            pa_code = parts[2]
            dim_code = parts[3]
            
            # Calculate correct questions
            correct_questions = calculate_question_range(pa_code, dim_code)
            
            # Update recommendations inside the rule
            if "recommendations" in rule:
                for rec in rule["recommendations"]:
                    current_qs = rec.get("questions", [])
                    if current_qs != correct_questions:
                        rec["questions"] = correct_questions
                        updates_count += 1
            
            # Update template question_range if present
            if "template" in rule and "question_range" in rule["template"]:
                 # This field might not exist in the provided snippet but good to check
                 pass

    # Update Integrity Section
    if "integrity" not in data:
        data["integrity"] = {}
    
    new_checksum = calculate_checksum(data)
    data["integrity"]["validation_checksum"] = new_checksum
    data["integrity"]["last_repair_date"] = datetime.now(timezone.utc).isoformat()
    data["integrity"]["repair_note"] = "Fixed PA-DIM question ID offsets"

    logger.info(f"Repaired {updates_count} rule entries.")
    logger.info(f"New Checksum: {new_checksum}")

    # Save back
    with open(RULES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info("File saved successfully.")

if __name__ == "__main__":
    repair_rules()