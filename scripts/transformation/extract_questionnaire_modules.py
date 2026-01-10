#!/usr/bin/env python3
"""
F.A.R.F.A.N Questionnaire Monolith Modularizer

Extracts questions from questionnaire_monolith.json and organizes them
into modular files by dimension, policy area, and cluster.

Version: 3.0.0
Author: FARFAN Restructuring Team
Date: 2026-01-01
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime

# Paths
MONOLITH_PATH = Path("canonic_questionnaire_central/questionnaire_monolith.json")
BASE_OUTPUT_PATH = Path("canonic_questionnaire_central")


class QuestionnaireModularizer:
    """Modularizes the questionnaire monolith into organized components."""

    def __init__(self, monolith_path: Path, output_path: Path):
        self.monolith_path = monolith_path
        self.output_path = output_path
        self.monolith = None
        self.index = {
            "version": "3.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "indices": {
                "by_dimension": {},
                "by_policy_area": {},
                "by_cluster": {},
                "by_base_slot": {},
                "by_scoring_modality": {},
                "by_question_id": {},
            },
        }

    def load_monolith(self) -> None:
        """Load the monolith JSON file."""
        print(f"Loading monolith from {self.monolith_path}...")
        with open(self.monolith_path, "r", encoding="utf-8") as f:
            self.monolith = json.load(f)
        print(
            f"Loaded {len(self.monolith.get('blocks', {}).get('micro_questions', []))} micro-questions"
        )

    def extract_dimensions(self) -> Dict[str, List[Dict]]:
        """Extract questions organized by dimension."""
        print("\n=== Extracting questions by dimension ===")
        dimension_questions = defaultdict(list)

        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])

        for q in micro_questions:
            dim_id = q.get("dimension_id")
            if dim_id:
                dimension_questions[dim_id].append(q)

        # Build index
        for dim_id, questions in dimension_questions.items():
            dim_names = {
                "DIM01": "DIM01_INSUMOS",
                "DIM02": "DIM02_ACTIVIDADES",
                "DIM03": "DIM03_PRODUCTOS",
                "DIM04": "DIM04_RESULTADOS",
                "DIM05": "DIM05_IMPACTOS",
                "DIM06": "DIM06_CAUSALIDAD",
            }
            dim_name = dim_names.get(dim_id, dim_id)
            self.index["indices"]["by_dimension"][dim_id] = {
                "file": f"dimensions/{dim_name}/questions.json",
                "count": len(questions),
                "question_ids": [q.get("question_id") for q in questions],
            }
            print(f"  {dim_id}: {len(questions)} questions")

        return dimension_questions

    def extract_policy_areas(self) -> Dict[str, List[Dict]]:
        """Extract questions organized by policy area."""
        print("\n=== Extracting questions by policy area ===")
        pa_questions = defaultdict(list)

        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])

        for q in micro_questions:
            pa_id = q.get("policy_area_id")
            if pa_id:
                pa_questions[pa_id].append(q)

        # Build index
        pa_names = {
            "PA01": "PA01_mujeres_genero",
            "PA02": "PA02_violencia_conflicto",
            "PA03": "PA03_ambiente_cambio_climatico",
            "PA04": "PA04_derechos_economicos_sociales_culturales",
            "PA05": "PA05_victimas_paz",
            "PA06": "PA06_ninez_adolescencia_juventud",
            "PA07": "PA07_tierras_territorios",
            "PA08": "PA08_lideres_defensores",
            "PA09": "PA09_crisis_PPL",
            "PA10": "PA10_migracion",
        }

        for pa_id, questions in pa_questions.items():
            pa_name = pa_names.get(pa_id, pa_id)
            self.index["indices"]["by_policy_area"][pa_id] = {
                "file": f"policy_areas/{pa_name}/questions.json",
                "count": len(questions),
                "question_ids": [q.get("question_id") for q in questions],
            }
            print(f"  {pa_id}: {len(questions)} questions")

        return pa_questions

    def extract_clusters(self) -> Dict[str, List[Dict]]:
        """Extract questions organized by cluster."""
        print("\n=== Extracting questions by cluster ===")
        cluster_questions = defaultdict(list)

        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])

        for q in micro_questions:
            cluster_id = q.get("cluster_id")
            if cluster_id:
                cluster_questions[cluster_id].append(q)

        # Build index
        cluster_names = {
            "CL01": "CL01_seguridad_paz",
            "CL02": "CL02_grupos_poblacionales",
            "CL03": "CL03_territorio_ambiente",
            "CL04": "CL04_derechos_sociales_crisis",
        }

        for cluster_id, questions in cluster_questions.items():
            cluster_name = cluster_names.get(cluster_id, cluster_id)
            self.index["indices"]["by_cluster"][cluster_id] = {
                "file": f"clusters/{cluster_name}/questions.json",
                "count": len(questions),
                "question_ids": [q.get("question_id") for q in questions],
            }
            print(f"  {cluster_id}: {len(questions)} questions")

        return cluster_questions

    def extract_base_slot_mapping(self) -> Dict[str, List[str]]:
        """Extract base_slot to question_id mapping."""
        print("\n=== Extracting base slot mappings ===")
        base_slot_map = defaultdict(list)

        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])

        for q in micro_questions:
            base_slot = q.get("base_slot")
            qid = q.get("question_id")
            if base_slot and qid:
                base_slot_map[base_slot].append(qid)

        for base_slot, qids in sorted(base_slot_map.items()):
            self.index["indices"]["by_base_slot"][base_slot] = qids
            print(f"  {base_slot}: {len(qids)} questions ({qids[0]}...{qids[-1]})")

        return base_slot_map

    def extract_scoring_modality_mapping(self) -> Dict[str, List[str]]:
        """Extract scoring modality to question_id mapping."""
        print("\n=== Extracting scoring modality mappings ===")
        modality_map = defaultdict(list)

        micro_questions = self.monolith.get("blocks", {}).get("micro_questions", [])

        for q in micro_questions:
            modality = q.get("scoring_modality")
            qid = q.get("question_id")
            if modality and qid:
                modality_map[modality].append(qid)

        for modality, qids in sorted(modality_map.items()):
            self.index["indices"]["by_scoring_modality"][modality] = {
                "count": len(qids),
                "question_ids": sorted(qids, key=lambda x: int(x[1:])),
            }
            print(f"  {modality}: {len(qids)} questions")

        return modality_map

    def save_dimension_files(self, dimension_questions: Dict[str, List[Dict]]) -> None:
        """Save dimension-specific question files."""
        print("\n=== Saving dimension files ===")
        dim_names = {
            "DIM01": "DIM01_INSUMOS",
            "DIM02": "DIM02_ACTIVIDADES",
            "DIM03": "DIM03_PRODUCTOS",
            "DIM04": "DIM04_RESULTADOS",
            "DIM05": "DIM05_IMPACTOS",
            "DIM06": "DIM06_CAUSALIDAD",
        }

        dim_info = (
            self.monolith.get("blocks", {}).get("niveles_abstraccion", {}).get("dimensions", [])
        )

        for dim_id, questions in dimension_questions.items():
            dim_name = dim_names.get(dim_id, dim_id)
            output_dir = self.output_path / "dimensions" / dim_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get dimension metadata
            dim_metadata = next((d for d in dim_info if d.get("dimension_id") == dim_id), {})

            # Save questions
            questions_file = output_dir / "questions.json"
            with open(questions_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "dimension_id": dim_id,
                        "dimension_metadata": dim_metadata,
                        "question_count": len(questions),
                        "questions": sorted(
                            questions, key=lambda x: int(x.get("question_id", "Q0")[1:])
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"  Saved {questions_file}")

            # Save dimension metadata
            metadata_file = output_dir / "metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(dim_metadata, f, indent=2, ensure_ascii=False)

    def save_policy_area_files(self, pa_questions: Dict[str, List[Dict]]) -> None:
        """Save policy area-specific question files."""
        print("\n=== Saving policy area files ===")
        pa_names = {
            "PA01": "PA01_mujeres_genero",
            "PA02": "PA02_violencia_conflicto",
            "PA03": "PA03_ambiente_cambio_climatico",
            "PA04": "PA04_derechos_economicos_sociales_culturales",
            "PA05": "PA05_victimas_paz",
            "PA06": "PA06_ninez_adolescencia_juventud",
            "PA07": "PA07_tierras_territorios",
            "PA08": "PA08_lideres_defensores",
            "PA09": "PA09_crisis_PPL",
            "PA10": "PA10_migracion",
        }

        canonical_notation = self.monolith.get("canonical_notation", {})
        pa_definitions = (
            self.monolith.get("blocks", {}).get("niveles_abstraccion", {}).get("policy_areas", [])
        )

        for pa_id, questions in pa_questions.items():
            pa_name = pa_names.get(pa_id, pa_id)
            output_dir = self.output_path / "policy_areas" / pa_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get policy area metadata from canonical notation
            pa_metadata = next((p for p in pa_definitions if p.get("policy_area_id") == pa_id), {})
            canonical_data = canonical_notation.get("policy_areas", {}).get(pa_id, {})

            # Combine metadata
            full_metadata = {**pa_metadata, "keywords": canonical_data.get("keywords", [])}

            # Save questions
            questions_file = output_dir / "questions.json"
            with open(questions_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "policy_area_id": pa_id,
                        "policy_area_metadata": full_metadata,
                        "question_count": len(questions),
                        "questions": sorted(
                            questions, key=lambda x: int(x.get("question_id", "Q0")[1:])
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"  Saved {questions_file}")

            # Save keywords
            keywords = canonical_data.get("keywords", [])
            if keywords:
                keywords_file = output_dir / "keywords.json"
                with open(keywords_file, "w", encoding="utf-8") as f:
                    json.dump({"keywords": keywords}, f, indent=2, ensure_ascii=False)

    def save_cluster_files(self, cluster_questions: Dict[str, List[Dict]]) -> None:
        """Save cluster-specific question files."""
        print("\n=== Saving cluster files ===")
        cluster_names = {
            "CL01": "CL01_seguridad_paz",
            "CL02": "CL02_grupos_poblacionales",
            "CL03": "CL03_territorio_ambiente",
            "CL04": "CL04_derechos_sociales_crisis",
        }

        cluster_definitions = (
            self.monolith.get("blocks", {}).get("niveles_abstraccion", {}).get("clusters", [])
        )

        for cluster_id, questions in cluster_questions.items():
            cluster_name = cluster_names.get(cluster_id, cluster_id)
            output_dir = self.output_path / "clusters" / cluster_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Get cluster metadata
            cluster_metadata = next(
                (c for c in cluster_definitions if c.get("cluster_id") == cluster_id), {}
            )

            # Save questions
            questions_file = output_dir / "questions.json"
            with open(questions_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "cluster_id": cluster_id,
                        "cluster_metadata": cluster_metadata,
                        "question_count": len(questions),
                        "questions": sorted(
                            questions, key=lambda x: int(x.get("question_id", "Q0")[1:])
                        ),
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            print(f"  Saved {questions_file}")

    def save_index(self) -> None:
        """Save the master index file."""
        index_file = self.output_path / "questionnaire_index.json"
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
        print(f"\n=== Saved index to {index_file} ===")

    def save_canonical_notation(self) -> None:
        """Save canonical notation separately."""
        notation_file = self.output_path / "canonical_notation.json"
        with open(notation_file, "w", encoding="utf-8") as f:
            json.dump(self.monolith.get("canonical_notation", {}), f, indent=2, ensure_ascii=False)
        print(f"=== Saved canonical notation to {notation_file} ===")

    def save_niveles_abstraccion(self) -> None:
        """Save niveles de abstraccion separately."""
        niveles_file = self.output_path / "niveles_abstraccion.json"
        with open(niveles_file, "w", encoding="utf-8") as f:
            json.dump(
                self.monolith.get("blocks", {}).get("niveles_abstraccion", {}),
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"=== Saved niveles de abstraccion to {niveles_file} ===")

    def save_meso_macro_questions(self) -> None:
        """Save meso and macro questions separately."""
        blocks = self.monolith.get("blocks", {})

        # Save macro question
        macro_file = self.output_path / "macro_question.json"
        with open(macro_file, "w", encoding="utf-8") as f:
            json.dump(blocks.get("macro_question", {}), f, indent=2, ensure_ascii=False)
        print(f"=== Saved macro question to {macro_file} ===")

        # Save meso questions
        meso_file = self.output_path / "meso_questions.json"
        with open(meso_file, "w", encoding="utf-8") as f:
            json.dump(blocks.get("meso_questions", []), f, indent=2, ensure_ascii=False)
        print(f"=== Saved meso questions to {meso_file} ===")

    def save_scoring_system(self) -> None:
        """Save scoring system separately."""
        scoring_file = self.output_path / "scoring" / "scoring_system.json"
        scoring_file.parent.mkdir(parents=True, exist_ok=True)
        with open(scoring_file, "w", encoding="utf-8") as f:
            json.dump(
                self.monolith.get("blocks", {}).get("scoring", {}), f, indent=2, ensure_ascii=False
            )
        print(f"=== Saved scoring system to {scoring_file} ===")

    def save_semantic_layers(self) -> None:
        """Save semantic layers separately."""
        semantic_file = self.output_path / "semantic" / "semantic_config.json"
        semantic_file.parent.mkdir(parents=True, exist_ok=True)
        with open(semantic_file, "w", encoding="utf-8") as f:
            json.dump(
                self.monolith.get("blocks", {}).get("semantic_layers", {}),
                f,
                indent=2,
                ensure_ascii=False,
            )
        print(f"=== Saved semantic layers to {semantic_file} ===")

    def create_new_monolith_stub(self) -> None:
        """Create a new lightweight monolith that references the modular files."""
        new_monolith = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "https://farfan-pipeline.org/schemas/questionnaire-monolith/v3.0.0.json",
            "schema_version": "3.0.0",
            "version": "3.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "modular": True,
            "modules": {
                "canonical_notation": "canonical_notation.json",
                "niveles_abstraccion": "niveles_abstraccion.json",
                "macro_question": "macro_question.json",
                "meso_questions": "meso_questions.json",
                "dimensions": {
                    "DIM01": "dimensions/DIM01_INSUMOS/questions.json",
                    "DIM02": "dimensions/DIM02_ACTIVIDADES/questions.json",
                    "DIM03": "dimensions/DIM03_PRODUCTOS/questions.json",
                    "DIM04": "dimensions/DIM04_RESULTADOS/questions.json",
                    "DIM05": "dimensions/DIM05_IMPACTOS/questions.json",
                    "DIM06": "dimensions/DIM06_CAUSALIDAD/questions.json",
                },
                "policy_areas": {
                    "PA01": "policy_areas/PA01_mujeres_genero/questions.json",
                    "PA02": "policy_areas/PA02_violencia_conflicto/questions.json",
                    "PA03": "policy_areas/PA03_ambiente_cambio_climatico/questions.json",
                    "PA04": "policy_areas/PA04_derechos_economicos_sociales_culturales/questions.json",
                    "PA05": "policy_areas/PA05_victimas_paz/questions.json",
                    "PA06": "policy_areas/PA06_ninez_adolescencia_juventud/questions.json",
                    "PA07": "policy_areas/PA07_tierras_territorios/questions.json",
                    "PA08": "policy_areas/PA08_lideres_defensores/questions.json",
                    "PA09": "policy_areas/PA09_crisis_PPL/questions.json",
                    "PA10": "policy_areas/PA10_migracion/questions.json",
                },
                "clusters": {
                    "CL01": "clusters/CL01_seguridad_paz/questions.json",
                    "CL02": "clusters/CL02_grupos_poblacionales/questions.json",
                    "CL03": "clusters/CL03_territorio_ambiente/questions.json",
                    "CL04": "clusters/CL04_derechos_sociales_crisis/questions.json",
                },
                "scoring": "scoring/scoring_system.json",
                "semantic": "semantic/semantic_config.json",
                "index": "questionnaire_index.json",
            },
            "integrity": self.monolith.get("integrity", {}),
            "observability": self.monolith.get("observability", {}),
        }

        new_monolith_file = self.output_path / "questionnaire_monolith_v3.json"
        with open(new_monolith_file, "w", encoding="utf-8") as f:
            json.dump(new_monolith, f, indent=2, ensure_ascii=False)
        print(f"=== Created new modular monolith stub at {new_monolith_file} ===")

    def run(self) -> None:
        """Execute the full modularization process."""
        print("=" * 60)
        print("F.A.R.F.A.N Questionnaire Monolith Modularizer v3.0.0")
        print("=" * 60)

        self.load_monolith()

        # Extract by different groupings
        dimension_questions = self.extract_dimensions()
        pa_questions = self.extract_policy_areas()
        cluster_questions = self.extract_clusters()
        self.extract_base_slot_mapping()
        self.extract_scoring_modality_mapping()

        # Save all files
        self.save_dimension_files(dimension_questions)
        self.save_policy_area_files(pa_questions)
        self.save_cluster_files(cluster_questions)
        self.save_canonical_notation()
        self.save_niveles_abstraccion()
        self.save_meso_macro_questions()
        self.save_scoring_system()
        self.save_semantic_layers()
        self.save_index()
        self.create_new_monolith_stub()

        print("\n" + "=" * 60)
        print("Modularization complete!")
        print(f"Index file: {self.output_path}/questionnaire_index.json")
        print("=" * 60)


def main():
    modularizer = QuestionnaireModularizer(
        monolith_path=MONOLITH_PATH, output_path=BASE_OUTPUT_PATH
    )
    modularizer.run()


if __name__ == "__main__":
    main()
