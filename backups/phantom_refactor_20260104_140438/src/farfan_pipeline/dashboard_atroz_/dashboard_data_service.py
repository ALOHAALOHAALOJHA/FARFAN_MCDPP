from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

logger = logging.getLogger(__name__)


class DashboardDataService:
    """Transforms pipeline artifacts into dashboard-friendly payloads."""

    def __init__(self, jobs_dir: Path) -> None:
        self.jobs_dir = jobs_dir

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def summarize_region(
        self,
        record: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Build lightweight region summary and context for downstream use."""
        report = self._load_report(record)
        macro_detail = self._extract_macro_detail(report, record)
        clusters = self._extract_clusters(report, record)
        scores = self._build_scores(record, macro_detail)
        indicators = self._build_indicators(record, macro_detail, scores, clusters)
        metadata = self._build_metadata(record, macro_detail)

        summary = {
            'id': record.get('id'),
            'job_id': record.get('job_id'),
            'name': (record.get('name') or '').upper(),
            'municipality': record.get('municipality'),
            'coordinates': self._build_coordinates(record),
            'metadata': metadata,
            'scores': scores,
            'clusterScores': {entry['cluster_id']: entry['score_percent'] for entry in clusters if entry.get('cluster_id')},
            'connections': list(record.get('connections') or []),
            'indicators': indicators,
            'macroBand': metadata.get('macroBand'),
            'updated_at': record.get('updated_at'),
        }

        context = {
            'report': report,
            'macro': macro_detail,
            'clusters': clusters,
        }
        return summary, context

    def build_region_detail(
        self,
        record: dict[str, Any],
        summary: dict[str, Any],
        context: dict[str, Any],
        region_evidence: Iterable[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Build full region payload with macro/meso/micro breakdown."""
        report = context.get('report') or {}
        macro_detail = context.get('macro') or self._extract_macro_detail(report, record)
        clusters = context.get('clusters') or self._extract_clusters(report, record)
        question_matrix = self._extract_question_matrix(report)
        recommendations = self._extract_recommendations(report, macro_detail, clusters)
        evidence_stream = self._merge_evidence(region_evidence, question_matrix, record)

        detailed = dict(summary)
        detailed['macro'] = macro_detail
        detailed['meso'] = clusters
        detailed['micro'] = question_matrix
        detailed['detailed_analysis'] = {
            'cluster_breakdown': self._to_cluster_breakdown(clusters),
            'question_matrix': question_matrix,
            'recommendations': recommendations,
            'evidence': evidence_stream,
        }
        return detailed

    def extract_question_matrix(self, report: dict[str, Any]) -> list[dict[str, Any]]:
        """Expose normalized question matrix for other services."""
        return self._extract_question_matrix(report)

    def normalize_evidence_stream(
        self,
        evidence: Iterable[dict[str, Any]],
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Normalize persisted evidence items for ticker display."""
        normalized = [self._normalize_evidence_item(item) for item in evidence if item]
        normalized = [item for item in normalized if item]
        normalized.sort(key=lambda item: item.get('timestamp') or '', reverse=True)
        return normalized[:limit]

    # ------------------------------------------------------------------
    # Report parsing helpers
    # ------------------------------------------------------------------

    def _load_report(self, record: dict[str, Any]) -> dict[str, Any]:
        """Load latest pipeline report for region if available."""
        job_id = record.get('latest_report') or record.get('job_id')
        candidate_paths: list[Path] = []

        report_path = record.get('report_path')
        if report_path:
            candidate_paths.append(Path(report_path))
        if job_id:
            candidate_paths.append(self.jobs_dir / f"{job_id}.json")

        for path in candidate_paths:
            if not path or not path.exists():
                continue
            try:
                with open(path, 'r', encoding='utf-8') as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    report = payload.get('report') if 'report' in payload else payload
                    if isinstance(report, dict):
                        return report
            except Exception as exc:  # pragma: no cover - best effort
                logger.warning("Failed to load dashboard report %s: %s", path, exc)
        return {}

    def _build_coordinates(self, record: dict[str, Any]) -> dict[str, float]:
        coords = record.get('coordinates') or {}
        x = self._first_number([coords.get('x'), coords.get('lng'), coords.get('lon')], default=50.0)
        y = self._first_number([coords.get('y'), coords.get('lat')], default=50.0)
        return {'x': float(x), 'y': float(y)}

    def _build_metadata(self, record: dict[str, Any], macro_detail: dict[str, Any]) -> dict[str, Any]:
        stats = dict(record.get('stats') or {})
        if 'departments' in stats and not isinstance(stats['departments'], list):
            stats['departments'] = list(self._ensure_list(stats['departments']))
        if macro_detail.get('band'):
            stats['macroBand'] = macro_detail['band']
        return stats

    def _build_scores(self, record: dict[str, Any], macro_detail: dict[str, Any]) -> dict[str, Any]:
        scores = dict(record.get('scores') or {})
        if macro_detail.get('score_percent') is not None:
            scores.setdefault('overall', macro_detail['score_percent'])
        scores.setdefault('lastUpdated', record.get('updated_at'))
        return scores

    def _build_indicators(
        self,
        record: dict[str, Any],
        macro_detail: dict[str, Any],
        scores: dict[str, Any],
        clusters: Sequence[dict[str, Any]],
    ) -> dict[str, Any]:
        if record.get('indicators'):
            return dict(record['indicators'])

        cluster_map = {entry['cluster_id'].lower(): entry for entry in clusters if entry.get('cluster_id')}
        alignment = macro_detail.get('score_percent')
        implementation = None
        impact = None
        if 'cl01' in cluster_map:
            implementation = cluster_map['cl01'].get('score_percent')
        implementation = implementation or scores.get('governance')
        if 'cl04' in cluster_map:
            impact = cluster_map['cl04'].get('score_percent')
        impact = impact or scores.get('environmental') or scores.get('social')

        return {
            'alignment': alignment,
            'implementation': implementation,
            'impact': impact,
        }

    def _extract_macro_detail(self, report: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
        macro_section: dict[str, Any] = {}
        if isinstance(report, dict):
            for key in ('macro_analysis', 'macro_summary', 'macro'):
                candidate = report.get(key)
                if isinstance(candidate, dict):
                    macro_section = candidate
                    break
        raw_scores = record.get('raw_scores') or {}
        percent_scores = record.get('scores') or {}

        score = self._first_number(
            [
                macro_section.get('overall_score'),
                macro_section.get('overall_posterior'),
                macro_section.get('adjusted_score'),
                raw_scores.get('overall'),
                self._maybe_percentage_to_fraction(percent_scores.get('overall')),
            ]
        )
        score_percent = self._first_number(
            [
                percent_scores.get('overall'),
                macro_section.get('overall_score_percent'),
                self._to_percent(score),
            ]
        )
        band = macro_section.get('quality_band') or macro_section.get('quality_level') or record.get('macro_band')
        coherence = self._first_number(
            [
                macro_section.get('cross_cutting_coherence'),
                macro_section.get('coherence'),
                macro_section.get('coherence_index'),
                macro_section.get('metadata', {}).get('coherence') if isinstance(macro_section.get('metadata'), dict) else None,
            ]
        )
        systemic_gaps = macro_section.get('systemic_gaps')
        if systemic_gaps is None and isinstance(macro_section.get('metadata'), dict):
            systemic_gaps = macro_section['metadata'].get('systemic_gaps')
        systemic_gaps = list(self._ensure_list(systemic_gaps)) if systemic_gaps else []
        alignment = self._first_number(
            [
                macro_section.get('strategic_alignment'),
                macro_section.get('alignment'),
            ]
        )

        return {
            'score': score,
            'score_percent': score_percent,
            'band': band,
            'coherence': coherence,
            'systemic_gaps': systemic_gaps,
            'alignment': alignment,
            'updated_at': record.get('updated_at'),
        }

    def _extract_clusters(
        self,
        report: dict[str, Any],
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Normalize cluster structures from report/state."""
        clusters: list[dict[str, Any]] = []
        cluster_section: Any = None

        if isinstance(report, dict):
            meso_section = report.get('meso_analysis')
            if isinstance(meso_section, dict):
                cluster_section = meso_section.get('cluster_scores') or meso_section.get('clusters')
            if cluster_section is None:
                cluster_section = report.get('meso_clusters')

        if isinstance(cluster_section, dict):
            for key, value in cluster_section.items():
                clusters.append(self._normalize_cluster_entry(value, key))
        elif isinstance(cluster_section, list):
            for entry in cluster_section:
                clusters.append(self._normalize_cluster_entry(entry))
        elif record.get('cluster_details'):
            for entry in record['cluster_details']:
                if isinstance(entry, dict):
                    clusters.append(self._normalize_cluster_entry(entry))

        if not clusters and record.get('cluster_scores'):
            for key, value in record['cluster_scores'].items():
                score_percent = self._sanitize_percent(value)
                score = self._maybe_percentage_to_fraction(score_percent)
                clusters.append(
                    {
                        'cluster_id': key,
                        'name': str(key).upper(),
                        'score': score,
                        'score_percent': score_percent,
                        'coherence': None,
                        'variance': None,
                        'areas': [],
                        'weakest_area': None,
                        'trend': 0.0,
                    }
                )

        clusters = [entry for entry in clusters if entry.get('cluster_id')]
        clusters.sort(key=lambda entry: entry.get('cluster_id'))
        return clusters

    def _normalize_cluster_entry(
        self,
        entry: Any,
        fallback_id: str | None = None,
    ) -> dict[str, Any]:
        if not isinstance(entry, dict):
            return {}
        cluster_id = entry.get('cluster_id') or entry.get('id') or fallback_id
        if not cluster_id:
            return {}
        name = entry.get('cluster_name') or entry.get('name') or str(cluster_id)
        score = self._first_number(
            [
                entry.get('adjusted_score'),
                entry.get('score'),
                entry.get('raw_meso_score'),
                entry.get('value'),
            ]
        )
        score_percent = self._first_number(
            [
                entry.get('score_percent'),
                self._to_percent(score),
            ]
        )
        coherence = self._first_number(
            [
                entry.get('coherence'),
                entry.get('metadata', {}).get('coherence') if isinstance(entry.get('metadata'), dict) else None,
                entry.get('dispersion_metrics', {}).get('coherence') if isinstance(entry.get('dispersion_metrics'), dict) else None,
            ]
        )
        variance = self._first_number(
            [
                entry.get('variance'),
                entry.get('dispersion_penalty'),
                entry.get('metadata', {}).get('variance') if isinstance(entry.get('metadata'), dict) else None,
            ]
        )
        areas = self._extract_cluster_areas(entry)
        weakest_area = entry.get('weakest_area')
        if not weakest_area and isinstance(entry.get('metadata'), dict):
            weakest_area = entry['metadata'].get('weakest_area')
        if not weakest_area and areas:
            weakest_area = areas[0]
        trend = self._first_number(
            [
                entry.get('trend'),
                entry.get('metadata', {}).get('trend') if isinstance(entry.get('metadata'), dict) else None,
            ],
            default=0.0,
        )

        return {
            'cluster_id': str(cluster_id),
            'name': str(name).upper(),
            'score': score,
            'score_percent': score_percent,
            'coherence': coherence,
            'variance': variance,
            'areas': areas,
            'weakest_area': weakest_area,
            'trend': trend,
        }

    def _extract_cluster_areas(self, entry: dict[str, Any]) -> list[str]:
        areas_field = entry.get('areas')
        if isinstance(areas_field, list):
            return [str(area) for area in areas_field]
        area_scores = entry.get('area_scores')
        if isinstance(area_scores, list):
            names: list[str] = []
            for area in area_scores:
                if not isinstance(area, dict):
                    continue
                candidate = area.get('policy_area_id') or area.get('policy_area') or area.get('name')
                if candidate:
                    names.append(str(candidate))
            return names
        return []

    def _extract_question_matrix(self, report: dict[str, Any]) -> list[dict[str, Any]]:
        questions_raw: list[dict[str, Any]] = []
        micro_section = report.get('micro_analysis') if isinstance(report, dict) else None
        if isinstance(micro_section, dict):
            if isinstance(micro_section.get('questions'), list):
                questions_raw.extend([item for item in micro_section['questions'] if isinstance(item, dict)])
            question_scores = micro_section.get('question_scores')
            if isinstance(question_scores, dict):
                for key, value in question_scores.items():
                    questions_raw.append({'question_id': key, 'score': value})
        micro_analyses = report.get('micro_analyses') if isinstance(report, dict) else None
        if isinstance(micro_analyses, list):
            questions_raw.extend([item for item in micro_analyses if isinstance(item, dict)])

        normalized: list[dict[str, Any]] = []
        for item in questions_raw:
            normalized_item = self._normalize_question_entry(item)
            if normalized_item:
                normalized.append(normalized_item)
        return normalized

    def _normalize_question_entry(self, item: dict[str, Any]) -> dict[str, Any] | None:
        question_id = item.get('question_id') or item.get('id') or item.get('code')
        if not question_id:
            return None
        text = item.get('text')
        if not text and isinstance(item.get('metadata'), dict):
            text = item['metadata'].get('title') or item['metadata'].get('question_text')
        text = text or f'Pregunta {question_id}'

        metadata = item.get('metadata') if isinstance(item.get('metadata'), dict) else {}
        policy_area = metadata.get('policy_area_id') or metadata.get('policy_area')
        dimension = metadata.get('dimension_id') or metadata.get('dimension')
        if not policy_area or not dimension:
            inferred_area, inferred_dimension = self._parse_question_identifier(str(question_id))
            policy_area = policy_area or inferred_area
            dimension = dimension or inferred_dimension

        score = self._first_number([
            item.get('score'),
            item.get('adjusted_score'),
            item.get('value'),
        ])
        score_percent = None
        if score is not None:
            if score <= 1.0:
                score_percent = self._to_percent(score)
            elif score <= 3.0:
                score_percent = self._sanitize_percent((score / 3.0) * 100.0)
            else:
                score_percent = self._sanitize_percent(score)

        evidence = self._normalize_evidence_list(item.get('evidence'), question_id)
        recommendations = self._normalize_recommendations(item.get('recommendations') or item.get('recommendation'))

        return {
            'id': str(question_id),
            'text': text,
            'score': score,
            'score_percent': score_percent,
            'category': policy_area,
            'dimension': dimension,
            'evidence': evidence,
            'recommendations': recommendations,
        }

    def _parse_question_identifier(self, identifier: str) -> tuple[str | None, str | None]:
        cleaned = identifier.replace('_', '-').upper()
        parts = cleaned.split('-')
        policy_area = None
        dimension = None
        for part in parts:
            if part.startswith('PA') and part[2:].isdigit():
                policy_area = part
            elif part.startswith('DIM') and part[3:].isdigit():
                dimension = part
            elif part.startswith('D') and part[1:].isdigit() and not dimension:
                dimension = f'DIM{part[1:]}'
        return policy_area, dimension

    def _normalize_recommendations(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    def _extract_recommendations(
        self,
        report: dict[str, Any],
        macro_detail: dict[str, Any],
        clusters: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        raw_recs = report.get('recommendations') if isinstance(report, dict) else None
        if isinstance(raw_recs, dict):
            items = raw_recs.get('items')
            raw_recs = items if isinstance(items, list) else list(raw_recs.values())
        recommendations: list[dict[str, Any]] = []
        if isinstance(raw_recs, list):
            for entry in raw_recs:
                normalized = self._normalize_recommendation_entry(entry)
                if normalized:
                    recommendations.append(normalized)
        elif raw_recs:
            normalized = self._normalize_recommendation_entry(raw_recs)
            if normalized:
                recommendations.append(normalized)

        if not recommendations:
            for gap in macro_detail.get('systemic_gaps') or []:
                recommendations.append(
                    {
                        'priority': 'ALTA',
                        'text': str(gap),
                        'category': 'MACRO',
                        'impact': 'HIGH',
                    }
                )
        if not recommendations and clusters:
            worst = min(
                (cluster for cluster in clusters if cluster.get('score_percent') is not None),
                key=lambda cluster: cluster['score_percent'],
                default=None,
            )
            if worst:
                recommendations.append(
                    {
                        'priority': 'MEDIA',
                        'text': f'Reforzar intervenciones en {worst["name"]}',
                        'category': 'MESO',
                        'impact': 'MEDIUM',
                    }
                )
        return recommendations

    def _normalize_recommendation_entry(self, entry: Any) -> dict[str, Any] | None:
        if isinstance(entry, dict):
            text = entry.get('description') or entry.get('text') or entry.get('message')
            if not text:
                return None
            severity = str(entry.get('severity') or entry.get('priority') or 'MEDIUM').upper()
            priority = self._severity_to_priority(severity)
            category = str(entry.get('category') or entry.get('type') or entry.get('source') or 'GENERAL').upper()
            impact = str(entry.get('impact') or severity).upper()
            return {
                'priority': priority,
                'text': text,
                'category': category,
                'impact': impact,
            }
        if entry:
            return {
                'priority': 'MEDIA',
                'text': str(entry),
                'category': 'GENERAL',
                'impact': 'MEDIUM',
            }
        return None

    def _merge_evidence(
        self,
        region_evidence: Iterable[dict[str, Any]] | None,
        question_matrix: Sequence[dict[str, Any]],
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        region_id = record.get('id')
        timestamp = record.get('updated_at') or datetime.now().isoformat()

        if region_evidence:
            for item in region_evidence:
                normalized = self._normalize_evidence_item(item, default_region_id=region_id)
                if not normalized:
                    continue
                key = (
                    normalized.get('source'),
                    normalized.get('page'),
                    normalized.get('text'),
                    normalized.get('question_id'),
                )
                if key in seen:
                    continue
                seen.add(key)
                merged.append(normalized)

        for question in question_matrix:
            for evidence in question.get('evidence') or []:
                normalized = dict(evidence)
                normalized.setdefault('region_id', region_id)
                normalized.setdefault('question_id', question.get('id'))
                normalized.setdefault('timestamp', timestamp)
                key = (
                    normalized.get('source'),
                    normalized.get('page'),
                    normalized.get('text'),
                    normalized.get('question_id'),
                )
                if key in seen:
                    continue
                seen.add(key)
                merged.append(normalized)

        merged.sort(key=lambda item: item.get('timestamp') or '', reverse=True)
        return merged[:200]

    def _normalize_evidence_list(
        self,
        evidence: Any,
        question_id: str | None,
    ) -> list[dict[str, Any]]:
        if evidence is None:
            return []
        items = evidence if isinstance(evidence, list) else [evidence]
        normalized: list[dict[str, Any]] = []
        for entry in items:
            normalized_entry = self._normalize_evidence_item(entry)
            if normalized_entry:
                normalized_entry.setdefault('question_id', question_id)
                normalized.append(normalized_entry)
        return normalized

    def _normalize_evidence_item(
        self,
        evidence: Any,
        default_region_id: str | None = None,
    ) -> dict[str, Any] | None:
        if isinstance(evidence, dict):
            source = evidence.get('source') or evidence.get('document') or 'Desconocido'
            page = self._safe_int(evidence.get('page') or evidence.get('page_number'))
            text = evidence.get('text') or evidence.get('excerpt') or evidence.get('content')
            if not text:
                return None
            timestamp = evidence.get('timestamp') or datetime.now().isoformat()
            normalized: dict[str, Any] = {
                'source': str(source),
                'page': page,
                'text': text,
                'timestamp': timestamp,
                'region_id': evidence.get('region_id') or default_region_id,
            }
            if 'relevance' in evidence:
                normalized['relevance'] = self._first_number([evidence.get('relevance')])
            if 'job_id' in evidence:
                normalized['job_id'] = evidence['job_id']
            if 'question_id' in evidence:
                normalized['question_id'] = evidence['question_id']
            return normalized
        if isinstance(evidence, str):
            return {
                'source': 'Documento',
                'page': None,
                'text': evidence,
                'timestamp': datetime.now().isoformat(),
                'region_id': default_region_id,
            }
        return None

    def _to_cluster_breakdown(self, clusters: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        breakdown: list[dict[str, Any]] = []
        for cluster in clusters:
            value = cluster.get('score_percent')
            if value is None and cluster.get('score') is not None:
                value = self._to_percent(cluster['score'])
            breakdown.append(
                {
                    'name': cluster.get('name') or cluster.get('cluster_id'),
                    'value': value,
                    'trend': cluster.get('trend', 0.0),
                    'weakest_area': cluster.get('weakest_area'),
                }
            )
        return breakdown

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def _severity_to_priority(self, severity: str) -> str:
        mapping = {
            'CRITICAL': 'CRITICA',
            'HIGH': 'ALTA',
            'MEDIUM': 'MEDIA',
            'LOW': 'BAJA',
        }
        return mapping.get(severity.upper(), severity.upper())

    def _safe_int(self, value: Any) -> int | None:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None

    def _first_number(self, candidates: Sequence[Any], default: float | None = None) -> float | None:
        for candidate in candidates:
            try:
                if candidate is None:
                    continue
                value = float(candidate)
                if not (value != value):  # NaN check
                    return value
            except (TypeError, ValueError):
                continue
        return default

    def _maybe_percentage_to_fraction(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if numeric > 1.0:
            return numeric / 100.0
        return numeric

    def _sanitize_percent(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        return round(numeric, 2)

    def _to_percent(self, value: Any) -> float | None:
        numeric = self._first_number([value])
        if numeric is None:
            return None
        if numeric <= 1.0:
            return round(numeric * 100.0, 2)
        return round(numeric, 2)

    def _ensure_list(self, value: Any) -> Iterable[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]
