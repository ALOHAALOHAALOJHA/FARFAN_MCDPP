import json
import os

# Paths
MASTER_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/artifacts/data/classification_master_v4.json"
CONTENT_PATH = "/Users/recovered/Downloads/F.A.R.F.A.N-MECHANISTIC_POLICY_PIPELINE_FINAL/artifacts/data/generic_questions_content.json"
OUTPUT_PATH = "src/farfan_pipeline/phases/Phase_two/epistemological_assets/PHASE2_CLASSIFICATION_MASTER_ENRICHED.json"

def generate_enriched():
    print(f"Loading master from {MASTER_PATH}...")
    with open(MASTER_PATH, 'r') as f:
        master = json.load(f)

    print(f"Loading content from {CONTENT_PATH}...")
    with open(CONTENT_PATH, 'r') as f:
        content_map = json.load(f)

    # Convert generic content to a list or easy lookup
    # content_map keys: "D1.Q1", "D1.Q2", etc.
    # We need to map Q001 -> D1.Q1, Q002 -> D1.Q2
    # Assuming standard sequence:
    # D1.Q1, D1.Q2, D1.Q3, D1.Q4, D1.Q5 (1-5)
    # D2.Q1 ...
    # ...
    # D6.Q5 (30)
    
    # Create ordered list of codes
    ordered_codes = []
    for d in range(1, 7):
        for q in range(1, 6):
            ordered_codes.append(f"D{d}.Q{q}")
            
    contracts = master.get("contracts", {})
    print(f"Found {len(contracts)} contracts in master.")
    
    enriched_count = 0
    
    # Iterate through Q001 to Q030
    for q_id in contracts:
        if q_id.startswith("Q") and len(q_id) == 4:
            try:
                num = int(q_id[1:]) # 1 to 30
                if 1 <= num <= 30:
                    code = ordered_codes[num-1]
                    if code in content_map:
                        # Extract text
                        text = content_map[code]["text"]
                        title = content_map[code]["title"]
                        
                        # Enrich
                        contracts[q_id]["question_text"] = text
                        contracts[q_id]["question_title"] = title
                        contracts[q_id]["generic_code"] = code
                        enriched_count += 1
            except ValueError:
                pass

    # Define Refined Strategies from User Input
    REFINED_STRATEGIES = {
        "TYPE_A": {
            "n1_strategy": {
                "name": "semantic_bundling",
                "operation": "Agrupa evidencia preservando contexto semántico",
                "differs_from_concat": "Mantiene metadata de fuente y contexto",
                "output": "Bundle con trazabilidad semántica",
                "example": {
                    "input": [
                        {"source": "DANE", "text": "tasa 45.3%", "context": "párrafo 12"},
                        {"source": "Med Legal", "text": "12 casos", "context": "tabla 3"}
                    ],
                    "output": {
                        "bundle_type": "semantic",
                        "facts": [],
                        "provenance": "preserved"
                    }
                }
            },
            "n2_strategy": {
                "name": "dempster_shafer",
                "operation": "Combina masas de probabilidad con gestión de conflicto",
                "rationale": "Maneja incertidumbre + conflicto semántico",
                "conflict_resolution": "Dempster's rule of combination"
            },
            "n3_fusion": {
                "name": "contradiction_veto",
                "operation": "Veto duro si contradicción semántica detectada",
                "formula": "if semantic_contradiction: confidence = 0.0"
            },
            "justification": "Bundling preserva contexto semántico"
        },
        "TYPE_B": {
            "n1_strategy": {
                "name": "evidence_concatenation",
                "operation": "Concatenación estándar pre-bayesiana",
                "rationale": "Prior + likelihood deben coexistir antes de update",
                "preserve": "concat es CORRECTO aquí",
                "output": "Array de evidencia heterogénea"
            },
            "n2_strategy": {
                "name": "bayesian_update",
                "operation": "P(H|E) = P(E|H) * P(H) / P(E)",
                "rationale": "Actualización bayesiana clásica",
                "no_change": "Ya está bien especificado"
            },
            "n3_fusion": {
                "name": "statistical_gate",
                "operation": "Veto si significancia estadística falla",
                "conditions": [
                    {"trigger": "p_value > 0.05", "action": "reduce_confidence", "multiplier": 0.5},
                    {"trigger": "sample_size < 30", "action": "flag_caution", "multiplier": 0.7}
                ]
            },
            "justification": "Concatenación pre-bayesiana legítima"
        },
        "TYPE_C": {
            "n1_strategy": {
                "name": "graph_element_collection",
                "operation": "Recolecta nodos, aristas y contextos para construcción de DAG",
                "rationale": "DAG construction requiere elementos simultáneos",
                "structure": {
                    "nodes": ["lista de entidades"],
                    "edges": ["lista de relaciones"],
                    "contexts": ["lista de condiciones"]
                }
            },
            "n2_strategy": {
                "name": "topological_overlay",
                "operation": "Fusiona grafos detectando ciclos y validando topología",
                "rationale": "Combina grafos parciales en estructura coherente",
                "validation": "Verifica acyclicity en cada fusión"
            },
            "n3_fusion": {
                "name": "cycle_detection_veto",
                "operation": "Veto TOTAL si ciclo detectado en DAG",
                "formula": "if has_cycle(DAG): confidence = 0.0; status = INVALID",
                "severity": "CRITICAL"
            },
            "justification": "Recolección para construcción de DAG"
        },
        "TYPE_D": {
            "n1_strategy": {
                "name": "financial_aggregation",
                "operation": "Agrega datos financieros con metadata de unidades",
                "differs_from_concat": "Preserva unidades y convierte a forma comparable",
                "normalization": {
                    "COP": "Convertir a % del presupuesto total",
                    "personas": "Convertir a % de población objetivo",
                    "metas": "Convertir a % de magnitud del problema"
                },
                "output": {
                    "values": [],
                    "units_normalized": True,
                    "base_reference": "presupuesto_total"
                }
            },
            "n2_strategy": {
                "name": "weighted_financial_mean",
                "operation": "Promedio ponderado con pesos EXPLÍCITOS",
                "differs_from_weighted_mean": "Pesos documentados y justificados",
                "weight_schema": {
                    "magnitud_problema": 0.4,
                    "suficiencia_presupuestal": 0.4,
                    "cobertura_meta": 0.2
                },
                "formula": "Σ(wi * vi_normalized) donde Σwi = 1.0",
                "transparency": "Pesos deben estar en contrato"
            },
            "n3_fusion": {
                "name": "sufficiency_gate",
                "operation": "Veto si presupuesto < umbral de viabilidad",
                "conditions": [
                    {"trigger": "budget_gap > 50%", "action": "block_branch", "multiplier": 0.0},
                    {"trigger": "budget_gap > 30%", "action": "reduce_confidence", "multiplier": 0.3}
                ]
            },
            "justification": "Agregación con pesos explícitos"
        },
        "TYPE_E": {
            "n1_strategy": {
                "name": "fact_collation",
                "operation": "Recolecta hechos para análisis de consistencia lógica",
                "rationale": "Gate lógico necesita ver TODOS los hechos",
                "preserve": "concat es correcto aquí (como audit dossier)"
            },
            "n2_strategy": {
                "name": "logical_consistency_check",
                "operation": "Verifica consistencia lógica SIN promediar",
                "differs_from_weighted_mean": "NO promedia contradicciones",
                "logic": "AND-based: todas las condiciones deben pasar",
                "formula": "consistency = min(c1, c2, ..., cn) NOT mean(c1, c2, ..., cn)",
                "output": {
                    "is_consistent": "boolean",
                    "violations": ["lista de contradicciones"],
                    "severity": "max(violation_severities)"
                }
            },
            "n3_fusion": {
                "name": "contradiction_dominance",
                "operation": "UNA contradicción domina TODO",
                "principle": "Lógica de Popper: una falsación invalida la teoría",
                "formula": "if any_contradiction: confidence = 0.0",
                "rationale": "Contradicciones NO son aditivas ni promediables",
                "examples": {
                    "Q014": "Desproporción actividad-meta → INVÁLIDO (no 'confianza media')",
                    "Q019": "Resultado no atiende problema → INVÁLIDO (no 'parcialmente válido')"
                }
            },
            "justification": "Colección para gate lógico"
        }
    }

    print(f"Enriched {enriched_count} contracts with text.")
    
    # Second pass: Enrich contracts with their specific refined strategies
    print("Injecting refined strategies into contracts...")
    for q_id, contract in contracts.items():
        c_type = contract.get("type")
        if c_type in REFINED_STRATEGIES:
            strat = REFINED_STRATEGIES[c_type]
            contract["n1_strategy_refined"] = strat["n1_strategy"]
            contract["n2_strategy_refined"] = strat["n2_strategy"]
            contract["n3_fusion_refined"] = strat["n3_fusion"]
            contract["epistemological_justification"] = strat["justification"]

    # Update master structure
    master["contracts"] = contracts
    master["refined_strategies"] = REFINED_STRATEGIES
    master["generic_questions_inventory"] = content_map
    
    print(f"Saving to {OUTPUT_PATH}...")
    
    # Ensure dir exists (already done via mkdir, but good practice)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    print("Done.")

if __name__ == "__main__":
    generate_enriched()
