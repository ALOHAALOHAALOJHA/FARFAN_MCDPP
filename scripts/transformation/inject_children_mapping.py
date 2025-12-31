import json
import os

MONOLITH_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/canonic_questionnaire_central/questionnaire_monolith.json"

def calculate_base_index(slot):
    # Slot format: "D{d}-Q{q}" e.g. "D1-Q1"
    # D1: 1-5, D2: 6-10 ... D6: 26-30
    try:
        parts = slot.split('-')
        d_num = int(parts[0].replace('D', ''))
        q_num = int(parts[1].replace('Q', ''))
        
        offset = (d_num - 1) * 5
        base_index = offset + q_num
        return base_index
    except Exception as e:
        print(f"Error parsing slot {slot}: {e}")
        return None

def inject_children():
    print(f"Loading monolith from {MONOLITH_PATH}...")
    try:
        with open(MONOLITH_PATH, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    micro_qs = data.get("blocks", {}).get("micro_questions", [])
    print(f"Found {len(micro_qs)} micro_questions.")

    count = 0
    for q in micro_qs:
        slot = q.get("base_slot")
        if slot and slot.startswith("D") and "-Q" in slot:
            base_index = calculate_base_index(slot)
            if base_index:
                # Generate children for 10 Policy Areas (0 to 9)
                # Q_id = base_index + (pa_index * 30)
                children = []
                for i in range(10):
                    q_val = base_index + (i * 30)
                    children.append(f"Q{q_val:03d}")
                
                q["children_questions"] = children
                count += 1
                # print(f"{slot} -> {children}")

    print(f"Injected children mapping into {count} questions.")
    
    if count > 0:
        print("Saving file...")
        try:
            with open(MONOLITH_PATH, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Save successful.")
        except Exception as e:
            print(f"Error saving: {e}")

if __name__ == "__main__":
    inject_children()
