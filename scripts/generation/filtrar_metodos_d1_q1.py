#!/usr/bin/env python3
"""
Filtra métodos del dispensario específicamente relevantes para D1-Q1.

D1-Q1 requiere:
- Extracción de datos numéricos (tasas, porcentajes, cifras)
- Verificación de línea base
- Presencia de año de referencia
- Mención de fuentes (DANE, Medicina Legal, Observatorio de Género)
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Patrones de búsqueda específicos para D1-Q1 (ampliados)
D1Q1_KEYWORDS = {
    "datos_numericos": [
        "extract.*number", "extract.*quantitative", "extract.*amount",
        "extract.*percentage", "extract.*rate", "extract.*tasa",
        "parse.*number", "quantitative.*claim", "numerical.*value",
        "financial.*amount", "extract.*financial", "extract.*numeric",
        "_extract.*amount", "_extract.*financial", "_parse.*amount",
        "extract.*claim", "extract.*value", "extract.*data",
        "number", "amount", "percentage", "rate", "tasa", "cifra"
    ],
    "linea_base": [
        "baseline", "linea.*base", "line.*base", "año.*base",
        "situación.*inicial", "diagnóstico", "diagnostico",
        "base.*line", "initial.*situation", "baseline.*data"
    ],
    "año_referencia": [
        "extract.*temporal", "extract.*year", "extract.*date",
        "temporal.*marker", "year.*reference", "año.*referencia",
        "parse.*temporal", "extract.*period", "extract.*time",
        "temporal", "year", "date", "period", "año", "vigencia",
        "_extract.*temporal", "_extract.*year", "_parse.*temporal"
    ],
    "fuentes": [
        "extract.*source", "extract.*fuente", "identify.*source",
        "source.*mention", "reference.*source", "extract.*reference",
        "source", "fuente", "reference", "referencia", "dane",
        "medicina.*legal", "observatorio"
    ],
    "validacion": [
        "validate", "verify", "check", "audit", "score", "evaluate"
    ]
}

def score_method_for_d1q1(method: Dict[str, Any]) -> float:
    """Calcula score de relevancia para D1-Q1"""
    score = 0.0
    
    method_name = method.get("method_name", "").lower()
    docstring = method.get("docstring", "").lower()
    text = f"{method_name} {docstring}"
    
    # Score por categoría
    for category, patterns in D1Q1_KEYWORDS.items():
        category_score = 0.0
        for pattern in patterns:
            import re
            if re.search(pattern, text, re.IGNORECASE):
                category_score += 0.25
        
        # Normalizar por categoría (máx 1.0)
        category_score = min(1.0, category_score)
        
        # Ponderar categorías
        weights = {
            "datos_numericos": 0.35,
            "linea_base": 0.20,
            "año_referencia": 0.20,
            "fuentes": 0.20,
            "validacion": 0.05
        }
        
        score += category_score * weights.get(category, 0.0)
    
    return score

def filter_methods_for_d1q1(report_path: Path) -> List[Dict[str, Any]]:
    """Filtra métodos relevantes para D1-Q1"""
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    methods = report.get("methods", [])
    
    # Calcular score D1-Q1 para cada método
    for method in methods:
        method["d1q1_score"] = score_method_for_d1q1(method)
    
    # Filtrar y ordenar
    relevant_methods = [
        m for m in methods
        if m["d1q1_score"] > 0.1  # Umbral mínimo
    ]
    
    relevant_methods.sort(key=lambda m: -m["d1q1_score"])
    
    return relevant_methods

def generate_d1q1_report(relevant_methods: List[Dict[str, Any]], output_path: Path):
    """Genera reporte específico para D1-Q1"""
    
    # Agrupar por nivel recomendado
    by_level = {
        "N1": [],
        "N2": [],
        "N3": []
    }
    
    for method in relevant_methods:
        level = method.get("recommended_level", "N1")
        if level in by_level:
            by_level[level].append(method)
    
    report = {
        "summary": {
            "total_relevant": len(relevant_methods),
            "by_level": {
                "N1": len(by_level["N1"]),
                "N2": len(by_level["N2"]),
                "N3": len(by_level["N3"])
            },
            "top_scoring": [
                {
                    "method": f"{m['class_name']}.{m['method_name']}",
                    "d1q1_score": round(m["d1q1_score"], 3),
                    "level": m["recommended_level"],
                    "file": m["file_path"]
                }
                for m in relevant_methods[:20]
            ]
        },
        "methods_by_level": {
            "N1": [
                {
                    "method": f"{m['class_name']}.{m['method_name']}",
                    "d1q1_score": round(m["d1q1_score"], 3),
                    "confidence": m["confidence"],
                    "n1_score": m["scores"]["N1"],
                    "file": m["file_path"],
                    "line_range": m["line_range"],
                    "docstring": m["docstring"][:150] + "..." if len(m["docstring"]) > 150 else m["docstring"]
                }
                for m in by_level["N1"][:30]
            ],
            "N2": [
                {
                    "method": f"{m['class_name']}.{m['method_name']}",
                    "d1q1_score": round(m["d1q1_score"], 3),
                    "confidence": m["confidence"],
                    "n2_score": m["scores"]["N2"],
                    "file": m["file_path"],
                    "line_range": m["line_range"],
                    "docstring": m["docstring"][:150] + "..." if len(m["docstring"]) > 150 else m["docstring"]
                }
                for m in by_level["N2"][:20]
            ],
            "N3": [
                {
                    "method": f"{m['class_name']}.{m['method_name']}",
                    "d1q1_score": round(m["d1q1_score"], 3),
                    "confidence": m["confidence"],
                    "n3_score": m["scores"]["N3"],
                    "file": m["file_path"],
                    "line_range": m["line_range"],
                    "docstring": m["docstring"][:150] + "..." if len(m["docstring"]) > 150 else m["docstring"]
                }
                for m in by_level["N3"][:20]
            ]
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def main():
    """Función principal"""
    report_path = Path("analisis_metodos_dispensario.json")
    
    if not report_path.exists():
        print(f"❌ No se encontró el reporte: {report_path}")
        print("   Ejecuta primero: python3 analizar_metodos_dispensario.py")
        return
    
    print("=" * 80)
    print("FILTRADO DE MÉTODOS PARA D1-Q1")
    print("=" * 80)
    print()
    
    relevant_methods = filter_methods_for_d1q1(report_path)
    
    print(f"✅ Encontrados {len(relevant_methods)} métodos relevantes para D1-Q1")
    
    # Generar reporte específico
    output_path = Path("metodos_relevantes_d1_q1.json")
    report = generate_d1q1_report(relevant_methods, output_path)
    
    print(f"\n📊 Reporte generado: {output_path}")
    print(f"\nResumen:")
    print(f"  Total relevantes: {report['summary']['total_relevant']}")
    print(f"  N1: {report['summary']['by_level']['N1']}")
    print(f"  N2: {report['summary']['by_level']['N2']}")
    print(f"  N3: {report['summary']['by_level']['N3']}")
    
    print("\n" + "=" * 80)
    print("TOP 15 MÉTODOS MÁS RELEVANTES PARA D1-Q1")
    print("=" * 80)
    
    for i, method in enumerate(relevant_methods[:15], 1):
        print(f"\n{i}. [{method['d1q1_score']:.3f}] {method['class_name']}.{method['method_name']}")
        print(f"   Nivel recomendado: {method['recommended_level']} (confianza: {method['confidence']:.3f})")
        print(f"   Scores: N1={method['scores']['N1']:.3f} N2={method['scores']['N2']:.3f} N3={method['scores']['N3']:.3f}")
        print(f"   Archivo: {Path(method['file_path']).name}:{method['line_range']}")
        if method['docstring']:
            print(f"   Docstring: {method['docstring'][:100]}...")

if __name__ == "__main__":
    main()

