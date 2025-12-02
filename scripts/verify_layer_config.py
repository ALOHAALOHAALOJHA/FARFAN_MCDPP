#!/usr/bin/env python3
import json
from pathlib import Path

config_file = Path(__file__).parent.parent / "config" / "canonic_inventorry_methods_layers.json"
data = json.load(open(config_file))

print(f'Total methods: {len(data["methods"])}')
print('All have 8 layers:', all(len(m["layers"]) == 8 for m in data["methods"].values()))
weight_check = all(abs(sum(m["weights"].values()) + sum(m["interaction_weights"].values()) - 1.0) < 0.01 for m in data["methods"].values())
print('All weights sum to 1.0:', weight_check)

for mid, m in list(data["methods"].items())[:3]:
    print(f'\nSample: {mid.split(".")[-1]}')
    print(f'  Layers: {len(m["layers"])}')
    print(f'  Weights sum: {sum(m["weights"].values()) + sum(m["interaction_weights"].values()):.3f}')
