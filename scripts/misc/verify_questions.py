import json
import os
import sys

FILE_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/canonic_questionnaire_central/questionnaire_monolith.json"

TARGET_STRINGS = [
    "Líneas base con fuente y desagregación",
    "brechas y vacíos de información",
    "Recursos presupuestales asignados al sector",
    "Capacidades institucionales para gestión del sector",
    "Justificación de alcance y competencias",
    "datos cuantitativos (tasas, porcentajes, cifras absolutas)",
    "reconoce explícitamente limitaciones en los datos",
]

def verify():
    print(f"Loading {FILE_PATH}...")
    try:
        with open(FILE_PATH, 'r') as f:
            content = f.read()
            data = json.loads(content)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print("File loaded successfully.")

    # 1. Search for texts in raw content
    print("\n--- 1. Raw String Search ---")
    found_any = False
    for s in TARGET_STRINGS:
        if s in content:
            print(f"[FOUND] String found: '{s}'")
            found_any = True
        else:
            print(f"[MISSING] String NOT found: '{s}'")
    
    if not found_any:
        print(">> No target strings found in the entire file.")

    # 2. Inspect Micro Questions Structure
    print("\n--- 2. Micro Questions Structure Inspection ---")
    micro_qs = data.get("blocks", {}).get("micro_questions", [])
    print(f"Found {len(micro_qs)} micro_questions.")

    question_slots = []
    text_fields_found = []

    for q in micro_qs:
        slot = q.get("base_slot")
        if slot and (slot.startswith("D1") or slot.startswith("D2") or slot.startswith("D3") or slot.startswith("D4") or slot.startswith("D5") or slot.startswith("D6")):
            question_slots.append(slot)
            # Check for new 'definition' object
            if "definition" in q:
                defn = q["definition"]
                if "title" in defn and "text" in defn:
                    text_fields_found.append(f"{slot}: Found definition '{defn['title']}'")
                else:
                    text_fields_found.append(f"{slot}: Found definition but MISSING title/text")
            else:
                 pass # Still missing?

    print(f"Identified {len(question_slots)} generic question slots (D1-D6).")
    if text_fields_found:
        print(f"Found text definitions in {len(text_fields_found)} slots.")
        # Print sample
        if len(text_fields_found) > 0:
            print("First 3 found:")
            print("\n".join(text_fields_found[:3]))
    else:
        print(">> NO definition fields found in any generic micro_question (D1-D6).")

if __name__ == "__main__":
    verify()
