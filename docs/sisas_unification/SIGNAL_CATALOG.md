# SISAS Signal Catalog

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

The Signal Catalog defines all 17 signal types used in the SISAS system. Signals are the primary mechanism for inter-component communication, carrying assessment data through the processing pipeline.

---

## 2. Signal Types Table

| signal_type | category | valid_phases | required_capabilities | empirical_availability_range |
|-------------|----------|--------------|----------------------|------------------------------|
| `EXTRACTION_RAW` | Extraction | [0] | `["extract_raw"]` | 0.95 - 1.00 |
| `EXTRACTION_PARSED` | Extraction | [0, 1] | `["parse_input", "assemble_components"]` | 0.90 - 0.98 |
| `EXTRACTION_NORMALIZED` | Extraction | [0, 1] | `["normalize", "structure_data"]` | 0.88 - 0.96 |
| `ASSEMBLY_COMPONENT` | Assembly | [1] | `["assemble_components"]` | 0.85 - 0.95 |
| `ASSEMBLY_MERGED` | Assembly | [1] | `["merge_fragments"]` | 0.82 - 0.93 |
| `ASSEMBLY_STRUCTURED` | Assembly | [1, 2] | `["structure_data", "enrich_context"]` | 0.80 - 0.92 |
| `ENRICHMENT_CONTEXT` | Enrichment | [2] | `["enrich_context"]` | 0.75 - 0.90 |
| `ENRICHMENT_METADATA` | Enrichment | [2] | `["enrich_metadata"]` | 0.78 - 0.92 |
| `ENRICHMENT_CROSS_REF` | Enrichment | [2, 3] | `["cross_reference", "validate_consistency"]` | 0.70 - 0.88 |
| `VALIDATION_SCHEMA` | Validation | [3] | `["validate_schema"]` | 0.92 - 0.99 |
| `VALIDATION_CONTENT` | Validation | [3] | `["validate_content"]` | 0.85 - 0.95 |
| `VALIDATION_CONSISTENCY` | Validation | [3, 4] | `["validate_consistency", "score_primary"]` | 0.80 - 0.92 |
| `SCORING_PRIMARY` | Scoring | [4] | `["score_primary"]` | 0.88 - 0.96 |
| `SCORING_WEIGHTED` | Scoring | [4, 5] | `["calculate_weights", "aggregate_scores"]` | 0.85 - 0.94 |
| `SCORING_NORMALIZED` | Scoring | [4, 5] | `["normalize_scores", "aggregate_scores"]` | 0.82 - 0.92 |
| `AGGREGATION_PARTIAL` | Aggregation | [5, 6] | `["aggregate_scores", "analyze_patterns"]` | 0.78 - 0.90 |
| `AGGREGATION_COMPLETE` | Aggregation | [5, 6, 7] | `["compute_totals", "generate_report"]` | 0.75 - 0.88 |
| `REPORT_DRAFT` | Report | [7] | `["generate_report"]` | 0.85 - 0.95 |
| `REPORT_FINAL` | Report | [7, 8, 9] | `["format_output", "finalize_assessment"]` | 0.90 - 0.98 |

---

## 3. Signal Categories

### 3.1 Extraction Category

Extraction signals carry raw and processed input data from source documents and forms.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `EXTRACTION_RAW` | Unprocessed raw input data | `raw_content`, `source_type`, `encoding` |
| `EXTRACTION_PARSED` | Parsed structured data | `parsed_data`, `parse_errors`, `schema_version` |
| `EXTRACTION_NORMALIZED` | Normalized data ready for assembly | `normalized_data`, `normalization_rules_applied` |

**Typical Flow:**
```
Input Source → EXTRACTION_RAW → EXTRACTION_PARSED → EXTRACTION_NORMALIZED → Assembly
```

---

### 3.2 Assembly Category

Assembly signals carry components being assembled into complete data structures.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `ASSEMBLY_COMPONENT` | Individual component data | `component_id`, `component_type`, `component_data` |
| `ASSEMBLY_MERGED` | Merged component fragments | `merged_components`, `merge_strategy`, `conflicts` |
| `ASSEMBLY_STRUCTURED` | Fully structured data | `structured_data`, `structure_schema`, `completeness` |

**Typical Flow:**
```
Normalized Data → ASSEMBLY_COMPONENT → ASSEMBLY_MERGED → ASSEMBLY_STRUCTURED → Enrichment
```

---

### 3.3 Enrichment Category

Enrichment signals carry contextual, metadata, and reference information.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `ENRICHMENT_CONTEXT` | Contextual information | `context_type`, `context_data`, `relevance_score` |
| `ENRICHMENT_METADATA` | Metadata attributes | `metadata_fields`, `source`, `timestamp` |
| `ENRICHMENT_CROSS_REF` | Cross-reference mappings | `references`, `reference_type`, `bidirectional` |

**Typical Flow:**
```
Structured Data → ENRICHMENT_CONTEXT → ENRICHMENT_METADATA → ENRICHMENT_CROSS_REF → Validation
```

---

### 3.4 Validation Category

Validation signals carry validation results and compliance status.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `VALIDATION_SCHEMA` | Schema validation results | `schema_id`, `valid`, `errors`, `warnings` |
| `VALIDATION_CONTENT` | Content validation results | `rules_checked`, `violations`, `auto_corrected` |
| `VALIDATION_CONSISTENCY` | Consistency check results | `checks_performed`, `inconsistencies`, `severity` |

**Typical Flow:**
```
Enriched Data → VALIDATION_SCHEMA → VALIDATION_CONTENT → VALIDATION_CONSISTENCY → Scoring
```

---

### 3.5 Scoring Category

Scoring signals carry calculated scores and weights.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `SCORING_PRIMARY` | Primary score calculation | `score`, `max_score`, `scoring_method`, `confidence` |
| `SCORING_WEIGHTED` | Weighted score with factors | `weighted_score`, `weights`, `factors` |
| `SCORING_NORMALIZED` | Normalized score (0-1 range) | `normalized_score`, `normalization_method`, `original_score` |

**Typical Flow:**
```
Validated Data → SCORING_PRIMARY → SCORING_WEIGHTED → SCORING_NORMALIZED → Aggregation
```

---

### 3.6 Aggregation Category

Aggregation signals carry aggregated scores across dimensions.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `AGGREGATION_PARTIAL` | Partial aggregation | `aggregation_level`, `partial_total`, `items_aggregated` |
| `AGGREGATION_COMPLETE` | Complete aggregation | `final_total`, `breakdown`, `aggregation_method` |

**Typical Flow:**
```
Normalized Scores → AGGREGATION_PARTIAL → AGGREGATION_COMPLETE → Reporting
```

---

### 3.7 Report Category

Report signals carry generated reports and final outputs.

| Signal Type | Description | Payload Fields |
|-------------|-------------|----------------|
| `REPORT_DRAFT` | Draft report for review | `report_content`, `format`, `sections`, `status` |
| `REPORT_FINAL` | Final approved report | `final_content`, `approval_status`, `signatures`, `hash` |

**Typical Flow:**
```
Aggregated Data → REPORT_DRAFT → Review → REPORT_FINAL → Finalization
```

---

## 4. JSON Schema for Signal

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://sisas.farfan.io/schemas/signal.json",
  "title": "SISAS Signal Schema",
  "description": "Schema for signals in the SISAS system",
  "type": "object",
  "required": ["signal_id", "signal_type", "source_phase", "target_scopes", "payload", "metadata", "created_at"],
  "properties": {
    "signal_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this signal (UUID v4)"
    },
    "signal_type": {
      "type": "string",
      "enum": [
        "EXTRACTION_RAW",
        "EXTRACTION_PARSED",
        "EXTRACTION_NORMALIZED",
        "ASSEMBLY_COMPONENT",
        "ASSEMBLY_MERGED",
        "ASSEMBLY_STRUCTURED",
        "ENRICHMENT_CONTEXT",
        "ENRICHMENT_METADATA",
        "ENRICHMENT_CROSS_REF",
        "VALIDATION_SCHEMA",
        "VALIDATION_CONTENT",
        "VALIDATION_CONSISTENCY",
        "SCORING_PRIMARY",
        "SCORING_WEIGHTED",
        "SCORING_NORMALIZED",
        "AGGREGATION_PARTIAL",
        "AGGREGATION_COMPLETE",
        "REPORT_DRAFT",
        "REPORT_FINAL"
      ],
      "description": "Type of signal from the catalog"
    },
    "source_phase": {
      "type": "integer",
      "minimum": 0,
      "maximum": 9,
      "description": "Phase that created this signal"
    },
    "target_scopes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "description": "Target scopes for this signal (PA, dimension, cluster, question)"
    },
    "payload": {
      "type": "object",
      "description": "Signal-type-specific payload data"
    },
    "metadata": {
      "type": "object",
      "required": ["trace_id", "correlation_id", "created_by"],
      "properties": {
        "trace_id": {
          "type": "string",
          "description": "Distributed tracing ID"
        },
        "correlation_id": {
          "type": "string",
          "description": "Correlation ID for related signals"
        },
        "created_by": {
          "type": "string",
          "description": "Component that created this signal"
        },
        "parent_signal_id": {
          "type": "string",
          "format": "uuid",
          "description": "ID of parent signal if derived"
        },
        "tags": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Optional tags for categorization"
        },
        "priority": {
          "type": "string",
          "enum": ["LOW", "NORMAL", "HIGH", "CRITICAL"],
          "default": "NORMAL"
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of signal creation"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when signal expires (default: created_at + 5 minutes)"
    },
    "version": {
      "type": "string",
      "default": "1.0.0",
      "description": "Signal schema version"
    }
  }
}
```

---

## 5. Example Signal Creation Code

### 5.1 Python Signal Creation

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid

class SignalType(Enum):
    # Extraction
    EXTRACTION_RAW = "EXTRACTION_RAW"
    EXTRACTION_PARSED = "EXTRACTION_PARSED"
    EXTRACTION_NORMALIZED = "EXTRACTION_NORMALIZED"
    # Assembly
    ASSEMBLY_COMPONENT = "ASSEMBLY_COMPONENT"
    ASSEMBLY_MERGED = "ASSEMBLY_MERGED"
    ASSEMBLY_STRUCTURED = "ASSEMBLY_STRUCTURED"
    # Enrichment
    ENRICHMENT_CONTEXT = "ENRICHMENT_CONTEXT"
    ENRICHMENT_METADATA = "ENRICHMENT_METADATA"
    ENRICHMENT_CROSS_REF = "ENRICHMENT_CROSS_REF"
    # Validation
    VALIDATION_SCHEMA = "VALIDATION_SCHEMA"
    VALIDATION_CONTENT = "VALIDATION_CONTENT"
    VALIDATION_CONSISTENCY = "VALIDATION_CONSISTENCY"
    # Scoring
    SCORING_PRIMARY = "SCORING_PRIMARY"
    SCORING_WEIGHTED = "SCORING_WEIGHTED"
    SCORING_NORMALIZED = "SCORING_NORMALIZED"
    # Aggregation
    AGGREGATION_PARTIAL = "AGGREGATION_PARTIAL"
    AGGREGATION_COMPLETE = "AGGREGATION_COMPLETE"
    # Report
    REPORT_DRAFT = "REPORT_DRAFT"
    REPORT_FINAL = "REPORT_FINAL"

class SignalPriority(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class SignalMetadata:
    trace_id: str
    correlation_id: str
    created_by: str
    parent_signal_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: SignalPriority = SignalPriority.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "created_by": self.created_by,
            "parent_signal_id": self.parent_signal_id,
            "tags": self.tags,
            "priority": self.priority.value
        }

@dataclass
class Signal:
    signal_type: SignalType
    source_phase: int
    target_scopes: List[str]
    payload: Dict[str, Any]
    metadata: SignalMetadata
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    version: str = "1.0.0"
    
    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(minutes=5)
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "source_phase": self.source_phase,
            "target_scopes": self.target_scopes,
            "payload": self.payload,
            "metadata": self.metadata.to_dict(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "version": self.version
        }

# Signal Factory for common signal types
class SignalFactory:
    """Factory for creating common signal types."""
    
    @staticmethod
    def create_extraction_raw(
        source_content: bytes,
        source_type: str,
        encoding: str,
        trace_id: str,
        target_scopes: List[str]
    ) -> Signal:
        """Create an EXTRACTION_RAW signal."""
        return Signal(
            signal_type=SignalType.EXTRACTION_RAW,
            source_phase=0,
            target_scopes=target_scopes,
            payload={
                "raw_content": source_content.decode(encoding) if isinstance(source_content, bytes) else source_content,
                "source_type": source_type,
                "encoding": encoding,
                "content_length": len(source_content)
            },
            metadata=SignalMetadata(
                trace_id=trace_id,
                correlation_id=str(uuid.uuid4()),
                created_by="phase_00_consumer",
                tags=["extraction", "raw"]
            )
        )
    
    @staticmethod
    def create_scoring_primary(
        question_id: str,
        score: float,
        max_score: float,
        scoring_method: str,
        confidence: float,
        trace_id: str,
        parent_signal_id: Optional[str] = None
    ) -> Signal:
        """Create a SCORING_PRIMARY signal."""
        return Signal(
            signal_type=SignalType.SCORING_PRIMARY,
            source_phase=4,
            target_scopes=[question_id],
            payload={
                "score": score,
                "max_score": max_score,
                "scoring_method": scoring_method,
                "confidence": confidence,
                "percentage": (score / max_score) * 100 if max_score > 0 else 0
            },
            metadata=SignalMetadata(
                trace_id=trace_id,
                correlation_id=str(uuid.uuid4()),
                created_by="phase_04_consumer",
                parent_signal_id=parent_signal_id,
                tags=["scoring", "primary"],
                priority=SignalPriority.HIGH
            )
        )
    
    @staticmethod
    def create_aggregation_complete(
        aggregation_level: str,
        total_score: float,
        breakdown: Dict[str, float],
        items_count: int,
        trace_id: str,
        target_scopes: List[str]
    ) -> Signal:
        """Create an AGGREGATION_COMPLETE signal."""
        return Signal(
            signal_type=SignalType.AGGREGATION_COMPLETE,
            source_phase=5,
            target_scopes=target_scopes,
            payload={
                "aggregation_level": aggregation_level,
                "final_total": total_score,
                "breakdown": breakdown,
                "items_aggregated": items_count,
                "aggregation_method": "weighted_average"
            },
            metadata=SignalMetadata(
                trace_id=trace_id,
                correlation_id=str(uuid.uuid4()),
                created_by="phase_05_consumer",
                tags=["aggregation", "complete"]
            )
        )
    
    @staticmethod
    def create_report_final(
        report_content: Dict[str, Any],
        format_type: str,
        approval_status: str,
        trace_id: str,
        target_scopes: List[str]
    ) -> Signal:
        """Create a REPORT_FINAL signal."""
        import hashlib
        content_hash = hashlib.sha256(
            str(report_content).encode()
        ).hexdigest()
        
        return Signal(
            signal_type=SignalType.REPORT_FINAL,
            source_phase=7,
            target_scopes=target_scopes,
            payload={
                "final_content": report_content,
                "format": format_type,
                "approval_status": approval_status,
                "signatures": [],
                "hash": content_hash
            },
            metadata=SignalMetadata(
                trace_id=trace_id,
                correlation_id=str(uuid.uuid4()),
                created_by="phase_07_consumer",
                tags=["report", "final"],
                priority=SignalPriority.CRITICAL
            )
        )

# Example usage
def example_signal_creation():
    """Demonstrate signal creation."""
    
    # Create a primary scoring signal
    scoring_signal = SignalFactory.create_scoring_primary(
        question_id="Q042",
        score=8.5,
        max_score=10.0,
        scoring_method="rubric_based",
        confidence=0.92,
        trace_id="trace-abc-123"
    )
    
    print(f"Created signal: {scoring_signal.signal_id}")
    print(f"Type: {scoring_signal.signal_type.value}")
    print(f"Payload: {scoring_signal.payload}")
    print(f"Expires: {scoring_signal.expires_at}")
    
    return scoring_signal
```

---

## 6. Signal Validation Rules

### 6.1 Structural Validation

All signals MUST pass these structural validations:

| Rule | Description |
|------|-------------|
| `SIGNAL_001` | `signal_id` must be a valid UUID v4 |
| `SIGNAL_002` | `signal_type` must be in the catalog |
| `SIGNAL_003` | `source_phase` must be 0-9 |
| `SIGNAL_004` | `target_scopes` must have at least one entry |
| `SIGNAL_005` | `payload` must be a non-empty object |
| `SIGNAL_006` | `metadata.trace_id` must be present |
| `SIGNAL_007` | `created_at` must be valid ISO 8601 |
| `SIGNAL_008` | `expires_at` must be after `created_at` |

### 6.2 Phase Validation

Signals can only be created by their valid source phases:

| Signal Type | Valid Source Phases |
|-------------|---------------------|
| `EXTRACTION_*` | Phase 0 |
| `ASSEMBLY_*` | Phase 1 |
| `ENRICHMENT_*` | Phase 2 |
| `VALIDATION_*` | Phase 3 |
| `SCORING_*` | Phase 4 |
| `AGGREGATION_*` | Phase 5 |
| `REPORT_*` | Phase 7 |

---

## 7. Empirical Availability

The `empirical_availability_range` indicates the typical success rate for each signal type based on historical data:

- **0.95-1.00:** Near-perfect availability (early pipeline signals)
- **0.85-0.95:** High availability (core processing signals)
- **0.75-0.85:** Moderate availability (complex enrichment/aggregation)
- **0.70-0.75:** Lower availability (cross-reference operations)

These ranges inform capacity planning and SLA definitions.

---

*End of Signal Catalog*
