import json
import os
import sys

# Paths
MONOLITH_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/canonic_questionnaire_central/questionnaire_monolith.json"
CONTENT_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/artifacts/data/generic_questions_content.json"

def inject_content():
    print(f"Loading content from {CONTENT_PATH}...")
    try:
        with open(CONTENT_PATH, 'r') as f:
            content_map = json.load(f)
    except Exception as e:
        print(f"Error loading content file: {e}")
        return

    print(f"Loading monolith from {MONOLITH_PATH}...")
    try:
        with open(MONOLITH_PATH, 'r') as f:
            monolith_data = json.load(f)
    except Exception as e:
        print(f"Error loading monolith file: {e}")
        return

    # Correct path: blocks -> micro_questions
    micro_qs = monolith_data.get("blocks", {}).get("micro_questions", [])
    print(f"Found {len(micro_qs)} micro_questions in monolith (under 'blocks').")
    
    if not micro_qs:
        # Fallback check if it's somewhere else
        print("Warning: No micro_questions found under 'blocks'. Checking root keys...")
        print(monolith_data.keys())
        return

    injected_count = 0
    
    # Iterate through content map (e.g., "D1.Q1": {...})
    for code, definition in content_map.items():
        # Convert "D1.Q1" -> "D1-Q1" for matching
        target_slot = code.replace(".", "-")
        
        # Find matching micro_question
        match = None
        for q in micro_qs:
            if q.get("base_slot") == target_slot:
                match = q
                break
        
        if match:
            # Inject definition object
            match["definition"] = {
                "title": definition["title"],
                "text": definition["text"],
                "code": code
            }
            injected_count += 1
            # print(f"Injecting into {target_slot}...") 
        else:
            print(f"WARNING: Slot {target_slot} not found in monolith.")

    print(f"\nTotal injected questions: {injected_count}")
    
    if injected_count > 0:
        print(f"Saving updated monolith to {MONOLITH_PATH}...")
        try:
            with open(MONOLITH_PATH, 'w') as f:
                json.dump(monolith_data, f, indent=2, ensure_ascii=False)
            print("Save successful.")
        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("No changes made.")

if __name__ == "__main__":
    inject_content()
