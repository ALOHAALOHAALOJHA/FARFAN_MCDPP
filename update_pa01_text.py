
import json
import sys

def update_questionnaire(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_texts = {
        "Q001": "¿El diagnóstico de las inequidades y brechas de género presenta datos cuantitativos (tasas de violencia basada en género, porcentajes de participación política, cifras de desempleo femenino o brecha salarial) con año de referencia y fuente identificada (Medicina Legal, DANE, Observatorio de Género), desagregados por territorio (rural/urbano) o grupos poblacionales (mujeres diversas, étnicas)?",
        "Q002": "¿El diagnóstico dimensiona numéricamente la magnitud de las desigualdades o violencias contra las mujeres y reconoce explícitamente limitaciones en los datos como 'subregistro de denuncias', 'información insuficiente sobre economía del cuidado', 'falta de caracterización de violencias no físicas' o 'vacíos en cifras municipales'?",
        "Q003": "¿El Plan Plurianual de Inversiones (PPI) o tablas presupuestales asignan recursos monetarios explícitos (en COP o millones $) a programas de prevención de violencias, funcionamiento de la Casa de la Mujer, estrategias de autonomía económica o transversalización del enfoque de género (Trazador Presupuestal de Género)?",
        "Q004": "¿El plan identifica las entidades responsables de la política de mujer y equidad (ej. Secretaría de la Mujer, Comisaría de Familia, mecanismos de género), describe sus capacidades (equipos psicosociales y jurídicos, duplas de atención) y señala limitaciones institucionales o necesidades de articulación con Fiscalía, ICBF o Gobernación?",
        "Q005": "¿El plan justifica el alcance de sus intervenciones en equidad de género mencionando el marco normativo (Ley 1257 de 2008, CONPES 4080) o reconociendo explícitamente qué competencias son municipales (prevención, atención inicial, rutas, empoderamiento) y cuáles dependen del nivel nacional (judicialización, protección material de alto riesgo)?",
        "Q006": "¿Las actividades para el cierre de brechas y atención a violencias (ej. operación de rutas de atención, escuelas de liderazgo político, formación en oficios no tradicionales, consejos de seguridad para mujeres) aparecen en formato estructurado (tabla, matriz, Plan Indicativo) con atributos verificables como responsable, producto esperado, cronograma y costo o presupuesto?",
        "Q007": "¿La descripción de actividades especifica el instrumento ('mediante Casas de la Mujer', 'a través de la Patrulla Púrpura', 'con capital semilla'), la población objetivo (mujeres rurales, víctimas de violencia, jefas de hogar) y explica cómo la actividad contribuye a la equidad ('para romper ciclos de dependencia', 'porque previene la feminización de la pobreza', 'con el fin de garantizar una vida libre de violencias')?",
        "Q008": "¿Las actividades propuestas se vinculan explícitamente con las causas estructurales de la desigualdad identificadas en el diagnóstico, tales como la dependencia económica, los estereotipos de género, la sobrecarga de cuidado o la debilidad en la respuesta institucional ante violencias?",
        "Q009": "¿El plan identifica posibles obstáculos o resistencias en la implementación de la política de género (ej. revictimización institucional, patrones culturales machistas arraigados, falta de denuncia por miedo) y propone medidas explícitas de mitigación o estrategias de cambio cultural para superarlos?",
        "Q010": "¿El plan describe explícitamente cómo las actividades de empoderamiento y prevención se complementan o siguen una secuencia lógica (ej. formación en derechos → empoderamiento económico → participación política; o sensibilización → denuncia → atención integral), evidenciando una estrategia articulada de transversalización?",
        "Q011": "¿Los indicadores de producto (mujeres atendidas en rutas de violencia, funcionarias/os capacitados en género, emprendimientos femeninos fortalecidos, lideresas formadas) incluyen línea base, meta cuantitativa y fuente de verificación?",
        "Q012": "¿Las metas de productos guardan relación con la magnitud de la brecha o violencia identificada en el diagnóstico, y se especifica la priorización (mujeres en riesgo de feminicidio, ruralidad dispersa) o la cobertura de la intervención frente a la demanda potencial?",
        "Q013": "¿Los productos están vinculados a códigos presupuestales específicos (Trazador de Género, recursos propios, SGP) y a entidades responsables identificadas (Secretaría de la Mujer, Desarrollo Social, Gobierno, Comisaría)?",
        "Q014": "¿Existe correspondencia factible entre el tipo de actividad (ej. 'una charla de sensibilización') y la magnitud de la meta del producto asociado (ej. 'reducción de la tolerancia social a la violencia'), considerando que los cambios en equidad requieren procesos sostenidos y no solo eventos puntuales?",
        "Q015": "¿El plan describe cómo los productos (ej. 'mujeres con autonomía económica', 'rutas de atención activas', 'Consejos Consultivos operando') generan o contribuyen a los resultados esperados (ej. 'reducción de brechas', 'garantía de derechos', 'empoderamiento real'), explicando esta conexión o ruta causal?",
        "Q016": "¿Los indicadores de resultado en materia de género (tasa de violencia intrafamiliar, brecha de desempleo por sexo, porcentaje de participación de mujeres en cargos directivos/elección, índice de desigualdad de género) están definidos con línea base, meta para 2027 y horizonte temporal del cuatrienio?",
        "Q017": "¿El plan describe la ruta que lleva a la igualdad y la garantía de derechos de las mujeres, mencionando condiciones necesarias o supuestos para que funcione (ej. 'si hay corresponsabilidad en el cuidado', 'si el mercado laboral absorbe la mano de obra femenina', 'si el sistema judicial no revictimiza')?",
        "Q018": "¿La ambición de las metas de resultado (ej. reducción de la VBG, aumento de la participación) se justifica en función de recursos asignados, capacidad institucional instalada (Comisarías, equipos), articulación con otros niveles, o se compara con la media nacional o municipios similares?",
        "Q019": "¿Los resultados propuestos (ej. 'vida libre de violencias', 'autonomía económica', 'participación incidente') atienden o abordan directamente las brechas, desigualdades y violencias priorizadas en el diagnóstico situacional de las mujeres?",
        "Q020": "¿El plan declara la alineación de sus resultados de género con la Política Pública Nacional de Equidad de Género, los Objetivos de Desarrollo Sostenible (especialmente ODS 5), o los lineamientos departamentales de mujer y género?",
        "Q021": "¿El plan define impactos o transformaciones estructurales de largo plazo para las mujeres (ej. 'transformación de roles de género', 'erradicación de la feminización de la pobreza', 'democracia paritaria consolidada'), describiendo cómo se llega a ellos desde los resultados y el horizonte temporal esperado más allá del cuatrienio?",
        "Q022": "¿Se utilizan índices reconocidos (ej. Índice de Paridad Política, Índice de Brecha Global de Género) o indicadores proxy para medir impactos en equidad, justificando por qué son adecuados para capturar las transformaciones culturales y estructurales esperadas?",
        "Q023": "¿Los impactos en equidad de género se alinean con marcos globales y consideran riesgos externos (retrocesos en derechos, crisis económicas que afectan desproporcionadamente a mujeres, aumento de violencias en contextos de inseguridad) que podrían impedir o revertir los logros esperados?",
        "Q024": "¿El plan evalúa si la ambición del impacto es realista, considerando posibles efectos no deseados (ej. doble jornada laboral sin redistribución del cuidado, violencia como reacción al empoderamiento) y propone un enfoque de \"acción sin daño\" o límites de la gestión municipal?",
        "Q025": "¿El plan describe cómo se sostendrán los logros en equidad de género más allá del periodo de gobierno, identificando mecanismos de institucionalización (ej. Política Pública Municipal por Acuerdo, transversalización presupuestal), apropiación por organizaciones de mujeres o fortalecimiento de la sociedad civil?",
        "Q026": "¿El plan presenta una descripción explícitamente de cómo se genera el cambio hacia la igualdad (ej. modelo ecológico para violencia, empoderamiento multidimensional), preferiblemente en diagrama o matriz, que identifique causas estructurales, intervenciones, supuestos y la secuencia insumos→actividades→productos→resultados→impactos?",
        "Q027": "¿El plan evita saltos desproporcionados en su lógica (ej. no asume que un taller elimina el machismo), reconociendo explícitamente que la transformación de inequidades de género requiere procesos culturales y estructurales sostenidos en el tiempo y no solo acciones afirmativas puntuales?",
        "Q028": "¿El plan reconoce la complejidad de las relaciones de género, identifica incertidumbres en su estrategia de cambio cultural, y propone mecanismos para aprender y ajustar (ej. observatorios de género, consejos consultivos activos, evaluaciones cualitativas)?",
        "Q029": "¿Se describe un sistema de monitoreo para la política de género que incluya indicadores desagregados, mecanismos de alerta temprana (ej. en violencias), retroalimentación con organizaciones de mujeres o Consejos Consultivos, y capacidad de adaptar la estrategia ante nuevas dinámicas de desigualdad?",
        "Q030": "¿El plan considera el contexto municipal específico (ruralidad, presencia de conflicto, vocación económica), reconoce la diversidad de las mujeres (enfoque interseccional: campesinas, afro, indígenas, con discapacidad) y explicita restricciones que condicionan el cierre de brechas en el territorio?"
    }

    micro_questions = data.get('blocks', {}).get('micro_questions', [])
    updated_count = 0
    for q in micro_questions:
        q_id = q.get('question_id')
        if q_id in new_texts:
            q['text'] = new_texts[q_id]
            updated_count += 1
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated {updated_count} questions in {file_path}")

if __name__ == '__main__':
    update_questionnaire(sys.argv[1])
