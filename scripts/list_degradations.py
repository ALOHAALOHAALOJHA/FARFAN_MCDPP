#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).parent.parent
with open(root / "METHODS_DISPENSARY_SIGNATURES_ENRICHED_FORENSIC.json") as f:
    data = json.load(f)

count = 0
for cls_name, cls_data in data.items():
    if cls_name in ["quality_metrics", "session_metadata"]:
        continue
    methods = cls_data.get("methods", {})
    for m_name, m_data in methods.items():
        ec = m_data.get("epistemological_classification", {})
        deg = ec.get("degradation")
        if deg:
            count += 1
            doc = (m_data.get("docstring") or "")[:80].replace("\n", " ")
            print(f"{count}. {cls_name}.{m_name}")
            print(f"   FROM: {deg['original_level']} -> TO: {deg['degraded_to']}")
            print(f"   REASON: {deg['reason']}")
            print(f"   RETURN: {m_data.get('return_type')}")
            print(f"   DOC: {doc}")
            print()

print(f"TOTAL: {count}")
