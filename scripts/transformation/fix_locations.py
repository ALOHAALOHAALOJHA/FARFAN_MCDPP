import json
import os

path_op = '/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE/METHODS_OPERACIONALIZACION.json'
path_map = '/Users/recovered/Applications/F.A.R.F.A.N -MECHANISTIC-PIPELINE/METHODS_TO_QUESTIONS_AND_FILES.json'

print(f"Loading {path_map} to revert changes...")
with open(path_map, 'r') as f:
    data_map = json.load(f)

reverted_count = 0
for key in data_map:
    if 'external_parameters' in data_map[key]:
        del data_map[key]['external_parameters']
        reverted_count += 1

print(f"Reverted {reverted_count} methods in {path_map}.")
with open(path_map, 'w') as f:
    json.dump(data_map, f, indent=2, ensure_ascii=False)


print(f"Loading {path_op} to add simplified instructions...")
with open(path_op, 'r') as f:
    data_op = json.load(f)

updated_op_count = 0
for method_name, content in data_op.items():
    if 'operacionalizacion' in content:
        op_data = content['operacionalizacion']
        params = op_data.get('parametros_configurables', [])
        
        simplified_params = []
        for p in params:
            default_val = p.get('default')
            is_mandatory = default_val is None
            
            # Create a clear string or object describing the requirement
            param_info = {
                "parametro": p.get('nombre'),
                "tipo": p.get('anotacion'),
                "es_obligatorio": is_mandatory,
                "modo_alimentacion": "EXTERNO_OBLIGATORIO" if is_mandatory else "CONFIGURACION_OPCIONAL"
            }
            if not is_mandatory:
                param_info["valor_por_defecto"] = default_val
            
            simplified_params.append(param_info)
        
        # Adding the new clear section
        op_data['requerimientos_integracion'] = simplified_params
        updated_op_count += 1

print(f"Updated {updated_op_count} methods in {path_op}.")
with open(path_op, 'w') as f:
    json.dump(data_op, f, indent=2, ensure_ascii=False)

print("Done.")
