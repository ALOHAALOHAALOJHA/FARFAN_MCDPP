#!/usr/bin/env python3
"""
Script para analizar métodos del dispensario y clasificarlos según criterios N1, N2, N3.

Evalúa métodos contra las condiciones ideales para cada nivel epistemológico.
"""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, field
import json

# ============================================================================
# CRITERIOS DE EVALUACIÓN
# ============================================================================

N1_CRITERIA = {
    "extraccion_literal": {
        "description": "El output debe poder trazarse a un span textual exacto",
        "keywords_positive": ["extract", "detect", "identify", "parse", "find", "get"],
        "keywords_negative": ["assess", "evaluate", "infer", "calculate", "score", "weight", "decide"],
        "patterns_positive": [r"span", r"offset", r"position", r"match", r"group"],
        "patterns_negative": [r"summary", r"normalize", r"interpret", r"classify.*relevance"]
    },
    "ausencia_inferencia": {
        "description": "No puede clasificar relevancia, asignar pesos, decidir suficiencia, inferir intención",
        "keywords_negative": ["classify", "weight", "sufficiency", "intention", "relevance", "importance"],
        "patterns_negative": [r"classify.*relevance", r"assign.*weight", r"decide.*sufficiency", r"infer.*intention"]
    },
    "rol_semantico": {
        "description": "Debe dejar claro qué tipo de cosa extrae (número, fecha, fuente, indicador)",
        "keywords_positive": ["number", "date", "source", "indicator", "temporal", "marker", "amount", "year"],
        "patterns_positive": [r"extract.*number", r"extract.*date", r"extract.*source", r"extract.*indicator"]
    },
    "no_colapsa_categorias": {
        "description": "No debe mezclar metas con diagnósticos, presupuestos con indicadores",
        "keywords_negative": ["meta.*diagnostico", "presupuesto.*indicador", "promedio.*tasa"],
        "patterns_negative": [r"meta.*diagnostico", r"presupuesto.*indicador"]
    },
    "output_estructurado": {
        "description": "Formato consistente, objetos atómicos (FACTs), no blobs",
        "keywords_positive": ["dict", "list", "tuple", "dataclass", "return.*dict", "return.*list"],
        "patterns_positive": [r"return\s+\{[^}]+\}", r"return\s+\[", r"->\s*dict", r"->\s*list"]
    },
    "neutralidad_epistemologica": {
        "description": "Nombre no debe sugerir causalidad, probabilidad, predicción, evaluación",
        "keywords_negative": ["causal", "bayesian", "probabilistic", "predict", "assess", "evaluate"],
        "patterns_negative": [r"causal", r"bayesian", r"probabilistic", r"predict", r"assess", r"evaluate"]
    }
}

N2_CRITERIA = {
    "dependencia_n1": {
        "description": "Debe declarar requires: ['raw_facts'] o similar",
        "keywords_positive": ["raw_facts", "requires", "depend", "input.*fact"],
        "patterns_positive": [r"requires.*raw_facts", r"depend.*fact"]
    },
    "validacion_logica": {
        "description": "Validación lógica, no estadística. Prohibido Bayes, scoring probabilístico",
        "keywords_positive": ["validate", "check", "verify", "coherence", "consistency", "eligibility"],
        "keywords_negative": ["bayesian", "probabilistic", "distribution", "confidence.*interval", "statistical"],
        "patterns_negative": [r"bayesian", r"probabilistic", r"distribution", r"confidence.*interval"]
    },
    "criterios_explicitos": {
        "description": "Criterios de aceptación y rechazo explícitos",
        "keywords_positive": ["if.*then", "condition", "criteria", "accept", "reject", "valid", "invalid"],
        "patterns_positive": [r"if\s+\w+\s+and\s+\w+", r"condition.*accept", r"criteria.*reject"]
    },
    "no_modifica_hechos": {
        "description": "Puede marcar/clasificar/etiquetar, pero no corregir números, imputar años, completar fuentes",
        "keywords_positive": ["mark", "classify", "label", "tag", "flag"],
        "keywords_negative": ["correct", "impute", "complete", "fix", "modify.*number", "change"],
        "patterns_negative": [r"correct.*number", r"impute.*year", r"complete.*source", r"fix.*data"]
    },
    "trazabilidad_conservada": {
        "description": "Toda decisión N2 debe referenciar los FACTs usados",
        "keywords_positive": ["reference", "trace", "fact", "evidence", "source.*fact"],
        "patterns_positive": [r"reference.*fact", r"trace.*evidence"]
    },
    "dominio_restringido": {
        "description": "Debe validar una cosa bien, no ser 'todólogo'",
        "keywords_positive": ["baseline", "temporal", "coherence", "co-occurrence"],
        "patterns_negative": [r"validate.*everything", r"check.*all"]
    }
}

N3_CRITERIA = {
    "asimetria_epistemologica": {
        "description": "N3 puede invalidar N1/N2, pero N1/N2 no pueden invalidar N3",
        "keywords_positive": ["audit", "invalidate", "reject", "fail", "pass", "compliance"],
        "patterns_positive": [r"audit", r"invalidate", r"compliance"]
    },
    "checklist_contractual": {
        "description": "Evaluación por checklist contractual, cada requisito corresponde a una condición",
        "keywords_positive": ["checklist", "requirement", "contract", "check.*requirement", "verify.*requirement"],
        "patterns_positive": [r"check.*requirement", r"verify.*requirement", r"checklist"]
    },
    "decision_binaria": {
        "description": "Output binario: YES/NO o PASS/FAIL, con justificación",
        "keywords_positive": ["pass", "fail", "yes", "no", "approved", "rejected", "binary"],
        "patterns_positive": [r"return\s+(True|False|pass|fail)", r"approved|rejected"]
    },
    "no_compensa_ausencias": {
        "description": "Un requisito faltante no puede ser compensado por abundancia en otros",
        "keywords_negative": ["compensate", "balance", "offset", "trade.*off"],
        "patterns_negative": [r"compensate.*absence", r"balance.*missing"]
    },
    "independencia_implementacion": {
        "description": "Debe operar igual con 1 método N1 o con 5, siempre que haya evidencia trazable",
        "keywords_positive": ["independent", "agnostic", "generic", "any.*method"],
        "patterns_positive": [r"independent.*method", r"agnostic.*implementation"]
    }
}

# ============================================================================
# CLASES DE DATOS
# ============================================================================

@dataclass
class MethodAnalysis:
    """Análisis de un método individual"""
    class_name: str
    method_name: str
    file_path: str
    docstring: str = ""
    code: str = ""
    line_start: int = 0
    line_end: int = 0
    
    # Scores por nivel
    n1_score: float = 0.0
    n2_score: float = 0.0
    n3_score: float = 0.0
    
    # Detalles de evaluación
    n1_details: Dict[str, Any] = field(default_factory=dict)
    n2_details: Dict[str, Any] = field(default_factory=dict)
    n3_details: Dict[str, Any] = field(default_factory=dict)
    
    # Recomendación
    recommended_level: str = ""
    confidence: float = 0.0

# ============================================================================
# ANALIZADOR DE MÉTODOS
# ============================================================================

class MethodAnalyzer:
    """Analiza métodos Python contra criterios N1, N2, N3"""
    
    def __init__(self):
        self.methods: List[MethodAnalysis] = []
    
    def extract_methods_from_file(self, file_path: Path) -> List[MethodAnalysis]:
        """Extrae métodos de un archivo Python"""
        methods = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Obtener clase padre si existe
                    class_name = None
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            for item in parent.body:
                                if item == node:
                                    class_name = parent.name
                                    break
                            if class_name:
                                break
                    
                    # Extraer información
                    method_name = node.name
                    docstring = ast.get_docstring(node) or ""
                    
                    # Obtener código fuente
                    code_lines = content.split('\n')
                    line_start = node.lineno
                    line_end = node.end_lineno if hasattr(node, 'end_lineno') else line_start
                    code = '\n'.join(code_lines[line_start-1:line_end])
                    
                    # Solo métodos que no son privados de clase (no empiezan con __)
                    if not method_name.startswith('__'):
                        method = MethodAnalysis(
                            class_name=class_name or "Module",
                            method_name=method_name,
                            file_path=str(file_path),
                            docstring=docstring,
                            code=code,
                            line_start=line_start,
                            line_end=line_end
                        )
                        methods.append(method)
        
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
        
        return methods
    
    def evaluate_n1(self, method: MethodAnalysis) -> Tuple[float, Dict[str, Any]]:
        """Evalúa método contra criterios N1"""
        score = 0.0
        max_score = len(N1_CRITERIA)
        details = {}
        
        text = f"{method.method_name} {method.docstring} {method.code}".lower()
        
        for criterion_name, criterion in N1_CRITERIA.items():
            criterion_score = 0.0
            criterion_details = {
                "passed": False,
                "reasons": []
            }
            
            # Verificar keywords positivos
            if "keywords_positive" in criterion:
                for keyword in criterion["keywords_positive"]:
                    if keyword.lower() in text:
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Keyword positivo encontrado: {keyword}")
            
            # Verificar patterns positivos
            if "patterns_positive" in criterion:
                for pattern in criterion["patterns_positive"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Pattern positivo encontrado: {pattern}")
            
            # Penalizar keywords negativos
            if "keywords_negative" in criterion:
                for keyword in criterion["keywords_negative"]:
                    if keyword.lower() in text:
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Keyword negativo encontrado: {keyword}")
            
            # Penalizar patterns negativos
            if "patterns_negative" in criterion:
                for pattern in criterion["patterns_negative"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Pattern negativo encontrado: {pattern}")
            
            # Normalizar score del criterio (0-1)
            criterion_score = max(0.0, min(1.0, criterion_score))
            criterion_details["passed"] = criterion_score >= 0.5
            criterion_details["score"] = criterion_score
            
            score += criterion_score
            details[criterion_name] = criterion_details
        
        # Score final normalizado
        final_score = score / max_score if max_score > 0 else 0.0
        
        return final_score, details
    
    def evaluate_n2(self, method: MethodAnalysis) -> Tuple[float, Dict[str, Any]]:
        """Evalúa método contra criterios N2"""
        score = 0.0
        max_score = len(N2_CRITERIA)
        details = {}
        
        text = f"{method.method_name} {method.docstring} {method.code}".lower()
        
        for criterion_name, criterion in N2_CRITERIA.items():
            criterion_score = 0.0
            criterion_details = {
                "passed": False,
                "reasons": []
            }
            
            # Verificar keywords positivos
            if "keywords_positive" in criterion:
                for keyword in criterion["keywords_positive"]:
                    if keyword.lower() in text:
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Keyword positivo encontrado: {keyword}")
            
            # Verificar patterns positivos
            if "patterns_positive" in criterion:
                for pattern in criterion["patterns_positive"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Pattern positivo encontrado: {pattern}")
            
            # Penalizar keywords negativos
            if "keywords_negative" in criterion:
                for keyword in criterion["keywords_negative"]:
                    if keyword.lower() in text:
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Keyword negativo encontrado: {keyword}")
            
            # Penalizar patterns negativos
            if "patterns_negative" in criterion:
                for pattern in criterion["patterns_negative"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Pattern negativo encontrado: {pattern}")
            
            # Normalizar score del criterio (0-1)
            criterion_score = max(0.0, min(1.0, criterion_score))
            criterion_details["passed"] = criterion_score >= 0.5
            criterion_details["score"] = criterion_score
            
            score += criterion_score
            details[criterion_name] = criterion_details
        
        # Score final normalizado
        final_score = score / max_score if max_score > 0 else 0.0
        
        return final_score, details
    
    def evaluate_n3(self, method: MethodAnalysis) -> Tuple[float, Dict[str, Any]]:
        """Evalúa método contra criterios N3"""
        score = 0.0
        max_score = len(N3_CRITERIA)
        details = {}
        
        text = f"{method.method_name} {method.docstring} {method.code}".lower()
        
        for criterion_name, criterion in N3_CRITERIA.items():
            criterion_score = 0.0
            criterion_details = {
                "passed": False,
                "reasons": []
            }
            
            # Verificar keywords positivos
            if "keywords_positive" in criterion:
                for keyword in criterion["keywords_positive"]:
                    if keyword.lower() in text:
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Keyword positivo encontrado: {keyword}")
            
            # Verificar patterns positivos
            if "patterns_positive" in criterion:
                for pattern in criterion["patterns_positive"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score += 0.3
                        criterion_details["reasons"].append(f"Pattern positivo encontrado: {pattern}")
            
            # Penalizar keywords negativos
            if "keywords_negative" in criterion:
                for keyword in criterion["keywords_negative"]:
                    if keyword.lower() in text:
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Keyword negativo encontrado: {keyword}")
            
            # Penalizar patterns negativos
            if "patterns_negative" in criterion:
                for pattern in criterion["patterns_negative"]:
                    if re.search(pattern, text, re.IGNORECASE):
                        criterion_score -= 0.5
                        criterion_details["reasons"].append(f"⚠️ Pattern negativo encontrado: {pattern}")
            
            # Normalizar score del criterio (0-1)
            criterion_score = max(0.0, min(1.0, criterion_score))
            criterion_details["passed"] = criterion_score >= 0.5
            criterion_details["score"] = criterion_score
            
            score += criterion_score
            details[criterion_name] = criterion_details
        
        # Score final normalizado
        final_score = score / max_score if max_score > 0 else 0.0
        
        return final_score, details
    
    def analyze_method(self, method: MethodAnalysis) -> MethodAnalysis:
        """Analiza un método completo"""
        # Evaluar contra cada nivel
        n1_score, n1_details = self.evaluate_n1(method)
        n2_score, n2_details = self.evaluate_n2(method)
        n3_score, n3_details = self.evaluate_n3(method)
        
        method.n1_score = n1_score
        method.n2_score = n2_score
        method.n3_score = n3_score
        method.n1_details = n1_details
        method.n2_details = n2_details
        method.n3_details = n3_details
        
        # Determinar nivel recomendado
        scores = {
            "N1": n1_score,
            "N2": n2_score,
            "N3": n3_score
        }
        
        recommended_level = max(scores.items(), key=lambda x: x[1])
        method.recommended_level = recommended_level[0]
        method.confidence = recommended_level[1]
        
        return method
    
    def scan_dispensary(self, dispensary_path: Path) -> List[MethodAnalysis]:
        """Escanea carpeta de dispensario y analiza todos los métodos"""
        all_methods = []
        
        # Buscar todos los archivos Python
        for py_file in dispensary_path.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            print(f"Procesando: {py_file.name}")
            methods = self.extract_methods_from_file(py_file)
            
            for method in methods:
                analyzed = self.analyze_method(method)
                all_methods.append(analyzed)
        
        self.methods = all_methods
        return all_methods
    
    def generate_report(self, output_path: Path):
        """Genera reporte JSON con análisis completo"""
        report = {
            "summary": {
                "total_methods": len(self.methods),
                "by_level": {
                    "N1": len([m for m in self.methods if m.recommended_level == "N1"]),
                    "N2": len([m for m in self.methods if m.recommended_level == "N2"]),
                    "N3": len([m for m in self.methods if m.recommended_level == "N3"])
                },
                "by_confidence": {
                    "high": len([m for m in self.methods if m.confidence >= 0.7]),
                    "medium": len([m for m in self.methods if 0.4 <= m.confidence < 0.7]),
                    "low": len([m for m in self.methods if m.confidence < 0.4])
                }
            },
            "methods": []
        }
        
        # Ordenar por score del nivel recomendado
        sorted_methods = sorted(
            self.methods,
            key=lambda m: (m.recommended_level, -m.confidence)
        )
        
        for method in sorted_methods:
            method_data = {
                "class_name": method.class_name,
                "method_name": method.method_name,
                "file_path": method.file_path,
                "line_range": f"{method.line_start}-{method.line_end}",
                "docstring": method.docstring[:200] + "..." if len(method.docstring) > 200 else method.docstring,
                "scores": {
                    "N1": round(method.n1_score, 3),
                    "N2": round(method.n2_score, 3),
                    "N3": round(method.n3_score, 3)
                },
                "recommended_level": method.recommended_level,
                "confidence": round(method.confidence, 3),
                "evaluation_details": {
                    "N1": {
                        k: {
                            "score": round(v["score"], 3),
                            "passed": v["passed"],
                            "reasons": v["reasons"][:5]  # Limitar razones
                        }
                        for k, v in method.n1_details.items()
                    },
                    "N2": {
                        k: {
                            "score": round(v["score"], 3),
                            "passed": v["passed"],
                            "reasons": v["reasons"][:5]
                        }
                        for k, v in method.n2_details.items()
                    },
                    "N3": {
                        k: {
                            "score": round(v["score"], 3),
                            "passed": v["passed"],
                            "reasons": v["reasons"][:5]
                        }
                        for k, v in method.n3_details.items()
                    }
                }
            }
            report["methods"].append(method_data)
        
        # Guardar reporte
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    dispensary_path = Path("src/farfan_pipeline/methods")
    
    if not dispensary_path.exists():
        print(f"❌ No se encontró la carpeta: {dispensary_path}")
        return
    
    print("=" * 80)
    print("ANÁLISIS DE MÉTODOS DEL DISPENSARIO")
    print("=" * 80)
    print()
    
    analyzer = MethodAnalyzer()
    methods = analyzer.scan_dispensary(dispensary_path)
    
    print(f"\n✅ Procesados {len(methods)} métodos")
    
    # Generar reporte
    output_path = Path("analisis_metodos_dispensario.json")
    report = analyzer.generate_report(output_path)
    
    print(f"\n📊 Reporte generado: {output_path}")
    print(f"\nResumen:")
    print(f"  Total métodos: {report['summary']['total_methods']}")
    print(f"  N1 recomendados: {report['summary']['by_level']['N1']}")
    print(f"  N2 recomendados: {report['summary']['by_level']['N2']}")
    print(f"  N3 recomendados: {report['summary']['by_level']['N3']}")
    print(f"\n  Alta confianza (≥0.7): {report['summary']['by_confidence']['high']}")
    print(f"  Media confianza (0.4-0.7): {report['summary']['by_confidence']['medium']}")
    print(f"  Baja confianza (<0.4): {report['summary']['by_confidence']['low']}")
    
    # Mostrar top métodos por nivel (bajar umbral a 0.3)
    print("\n" + "=" * 80)
    print("TOP MÉTODOS POR NIVEL (confianza ≥ 0.3)")
    print("=" * 80)
    
    for level in ["N1", "N2", "N3"]:
        level_methods = [
            m for m in methods
            if m.recommended_level == level and m.confidence >= 0.3
        ]
        level_methods.sort(key=lambda m: -m.confidence)
        
        print(f"\n{level} ({len(level_methods)} métodos, mostrando top 15):")
        for method in level_methods[:15]:  # Top 15
            print(f"  [{method.confidence:.3f}] {method.class_name}.{method.method_name}")
            print(f"      Archivo: {Path(method.file_path).name}:{method.line_start}")
            print(f"      Scores: N1={method.n1_score:.3f} N2={method.n2_score:.3f} N3={method.n3_score:.3f}")
    
    # Mostrar métodos con mejor score absoluto por nivel (sin importar nivel recomendado)
    print("\n" + "=" * 80)
    print("MEJORES MÉTODOS POR SCORE ABSOLUTO (sin importar nivel recomendado)")
    print("=" * 80)
    
    # Top N1 por score N1
    n1_by_score = sorted(methods, key=lambda m: -m.n1_score)[:10]
    print("\nTop 10 por score N1:")
    for method in n1_by_score:
        print(f"  [{method.n1_score:.3f}] {method.class_name}.{method.method_name} (recomendado: {method.recommended_level})")
    
    # Top N2 por score N2
    n2_by_score = sorted(methods, key=lambda m: -m.n2_score)[:10]
    print("\nTop 10 por score N2:")
    for method in n2_by_score:
        print(f"  [{method.n2_score:.3f}] {method.class_name}.{method.method_name} (recomendado: {method.recommended_level})")
    
    # Top N3 por score N3
    n3_by_score = sorted(methods, key=lambda m: -m.n3_score)[:10]
    print("\nTop 10 por score N3:")
    for method in n3_by_score:
        print(f"  [{method.n3_score:.3f}] {method.class_name}.{method.method_name} (recomendado: {method.recommended_level})")

if __name__ == "__main__":
    main()

