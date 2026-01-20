# SISAS Consumer Registry Specification

**Version:** 1.0.0  
**Date:** 2026-01-19  
**Status:** CANONICAL  

---

## 1. Overview

The Consumer Registry is the authoritative source for all phase consumers in the SISAS system. Each consumer is uniquely identified, declares its processing capabilities, and specifies which signal types it can handle.

---

## 2. Consumer Table

The following table defines all 10 phase consumers with their complete specifications:

| consumer_id | phase | scopes | capabilities | signal_types |
|-------------|-------|--------|--------------|--------------|
| `phase_00_consumer` | 0 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["extract_raw", "parse_input", "tokenize", "normalize"]` | `["EXTRACTION_RAW", "EXTRACTION_PARSED", "EXTRACTION_NORMALIZED"]` |
| `phase_01_consumer` | 1 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["assemble_components", "merge_fragments", "structure_data", "validate_assembly"]` | `["ASSEMBLY_COMPONENT", "ASSEMBLY_MERGED", "ASSEMBLY_STRUCTURED"]` |
| `phase_02_consumer` | 2 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["enrich_context", "enrich_metadata", "enrich_references", "cross_reference"]` | `["ENRICHMENT_CONTEXT", "ENRICHMENT_METADATA", "ENRICHMENT_CROSS_REF"]` |
| `phase_03_consumer` | 3 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["validate_schema", "validate_content", "validate_consistency", "check_constraints"]` | `["VALIDATION_SCHEMA", "VALIDATION_CONTENT", "VALIDATION_CONSISTENCY"]` |
| `phase_04_consumer` | 4 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["score_primary", "score_secondary", "calculate_weights", "normalize_scores"]` | `["SCORING_PRIMARY", "SCORING_WEIGHTED", "SCORING_NORMALIZED"]` |
| `phase_05_consumer` | 5 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["aggregate_scores", "aggregate_by_dimension", "aggregate_by_cluster", "compute_totals"]` | `["AGGREGATION_PARTIAL", "AGGREGATION_COMPLETE"]` |
| `phase_06_consumer` | 6 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["analyze_patterns", "detect_anomalies", "compute_statistics", "generate_insights"]` | `["ANALYSIS_PATTERN", "ANALYSIS_ANOMALY", "ANALYSIS_STATISTICAL"]` |
| `phase_07_consumer` | 7 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["generate_report", "format_output", "create_visualizations", "compile_summary"]` | `["REPORT_DRAFT", "REPORT_FINAL"]` |
| `phase_08_consumer` | 8 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["integrate_external", "sync_data", "export_results", "archive_state"]` | `["INTEGRATION_SYNC", "INTEGRATION_EXPORT"]` |
| `phase_09_consumer` | 9 | `{"policy_areas": ["PA01-PA10"], "dimensions": ["D1-D6"], "clusters": ["CL1-CL4"], "questions": ["Q001-Q300"]}` | `["finalize_assessment", "seal_results", "generate_attestation", "cleanup"]` | `["FINALIZATION_SEAL", "FINALIZATION_ATTESTATION"]` |

---

## 3. Consumer Details

### 3.1 Phase 00 Consumer: Extraction

**Purpose:** Extracts raw data from input sources and normalizes it for downstream processing.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_00_consumer` |
| phase | 0 |
| priority | HIGHEST |
| max_concurrent | 10 |
| timeout_ms | 30000 |

**Capabilities:**
- `extract_raw`: Extract unprocessed data from input
- `parse_input`: Parse structured/semi-structured input formats
- `tokenize`: Break input into processable tokens
- `normalize`: Standardize data formats and encodings

**Signal Types Handled:**
- `EXTRACTION_RAW`: Raw input data signals
- `EXTRACTION_PARSED`: Parsed data structures
- `EXTRACTION_NORMALIZED`: Normalized data ready for assembly

---

### 3.2 Phase 01 Consumer: Assembly

**Purpose:** Assembles extracted components into coherent data structures.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_01_consumer` |
| phase | 1 |
| priority | HIGH |
| max_concurrent | 8 |
| timeout_ms | 45000 |

**Capabilities:**
- `assemble_components`: Combine extracted components
- `merge_fragments`: Merge fragmented data pieces
- `structure_data`: Create structured representations
- `validate_assembly`: Verify assembly completeness

**Signal Types Handled:**
- `ASSEMBLY_COMPONENT`: Individual component signals
- `ASSEMBLY_MERGED`: Merged fragment signals
- `ASSEMBLY_STRUCTURED`: Fully structured data signals

---

### 3.3 Phase 02 Consumer: Enrichment

**Purpose:** Enriches assembled data with context, metadata, and cross-references.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_02_consumer` |
| phase | 2 |
| priority | HIGH |
| max_concurrent | 12 |
| timeout_ms | 60000 |

**Capabilities:**
- `enrich_context`: Add contextual information
- `enrich_metadata`: Attach metadata attributes
- `enrich_references`: Add reference links
- `cross_reference`: Create cross-reference mappings

**Signal Types Handled:**
- `ENRICHMENT_CONTEXT`: Context enrichment signals
- `ENRICHMENT_METADATA`: Metadata enrichment signals
- `ENRICHMENT_CROSS_REF`: Cross-reference signals

---

### 3.4 Phase 03 Consumer: Validation

**Purpose:** Validates data against schemas, content rules, and consistency constraints.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_03_consumer` |
| phase | 3 |
| priority | HIGH |
| max_concurrent | 6 |
| timeout_ms | 30000 |

**Capabilities:**
- `validate_schema`: Validate against JSON/data schemas
- `validate_content`: Verify content correctness
- `validate_consistency`: Check internal consistency
- `check_constraints`: Enforce business constraints

**Signal Types Handled:**
- `VALIDATION_SCHEMA`: Schema validation signals
- `VALIDATION_CONTENT`: Content validation signals
- `VALIDATION_CONSISTENCY`: Consistency check signals

---

### 3.5 Phase 04 Consumer: Scoring

**Purpose:** Calculates primary and weighted scores for assessment items.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_04_consumer` |
| phase | 4 |
| priority | MEDIUM |
| max_concurrent | 8 |
| timeout_ms | 45000 |

**Capabilities:**
- `score_primary`: Calculate primary scores
- `score_secondary`: Calculate secondary/derived scores
- `calculate_weights`: Compute scoring weights
- `normalize_scores`: Normalize scores to standard range

**Signal Types Handled:**
- `SCORING_PRIMARY`: Primary score signals
- `SCORING_WEIGHTED`: Weighted score signals
- `SCORING_NORMALIZED`: Normalized score signals

---

### 3.6 Phase 05 Consumer: Aggregation

**Purpose:** Aggregates scores across dimensions, clusters, and policy areas.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_05_consumer` |
| phase | 5 |
| priority | MEDIUM |
| max_concurrent | 4 |
| timeout_ms | 60000 |

**Capabilities:**
- `aggregate_scores`: Combine individual scores
- `aggregate_by_dimension`: Aggregate by dimension
- `aggregate_by_cluster`: Aggregate by cluster
- `compute_totals`: Calculate grand totals

**Signal Types Handled:**
- `AGGREGATION_PARTIAL`: Partial aggregation signals
- `AGGREGATION_COMPLETE`: Complete aggregation signals

---

### 3.7 Phase 06 Consumer: Analysis

**Purpose:** Analyzes aggregated data for patterns, anomalies, and insights.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_06_consumer` |
| phase | 6 |
| priority | MEDIUM |
| max_concurrent | 6 |
| timeout_ms | 90000 |

**Capabilities:**
- `analyze_patterns`: Detect patterns in data
- `detect_anomalies`: Identify anomalous values
- `compute_statistics`: Calculate statistical measures
- `generate_insights`: Produce analytical insights

**Signal Types Handled:**
- `ANALYSIS_PATTERN`: Pattern analysis signals
- `ANALYSIS_ANOMALY`: Anomaly detection signals
- `ANALYSIS_STATISTICAL`: Statistical analysis signals

---

### 3.8 Phase 07 Consumer: Reporting

**Purpose:** Generates reports, visualizations, and summary outputs.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_07_consumer` |
| phase | 7 |
| priority | LOW |
| max_concurrent | 4 |
| timeout_ms | 120000 |

**Capabilities:**
- `generate_report`: Create report documents
- `format_output`: Format output for consumption
- `create_visualizations`: Generate visual representations
- `compile_summary`: Compile executive summaries

**Signal Types Handled:**
- `REPORT_DRAFT`: Draft report signals
- `REPORT_FINAL`: Final report signals

---

### 3.9 Phase 08 Consumer: Integration

**Purpose:** Integrates with external systems and exports results.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_08_consumer` |
| phase | 8 |
| priority | LOW |
| max_concurrent | 4 |
| timeout_ms | 180000 |

**Capabilities:**
- `integrate_external`: Connect to external systems
- `sync_data`: Synchronize data with external stores
- `export_results`: Export results in various formats
- `archive_state`: Archive assessment state

**Signal Types Handled:**
- `INTEGRATION_SYNC`: Synchronization signals
- `INTEGRATION_EXPORT`: Export signals

---

### 3.10 Phase 09 Consumer: Finalization

**Purpose:** Finalizes assessments, seals results, and generates attestations.

| Attribute | Value |
|-----------|-------|
| consumer_id | `phase_09_consumer` |
| phase | 9 |
| priority | HIGHEST |
| max_concurrent | 2 |
| timeout_ms | 60000 |

**Capabilities:**
- `finalize_assessment`: Complete the assessment process
- `seal_results`: Cryptographically seal results
- `generate_attestation`: Create attestation records
- `cleanup`: Clean up temporary resources

**Signal Types Handled:**
- `FINALIZATION_SEAL`: Result sealing signals
- `FINALIZATION_ATTESTATION`: Attestation signals

---

## 4. JSON Schema for Consumer Registration

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://sisas.farfan.io/schemas/consumer-registration.json",
  "title": "SISAS Consumer Registration Schema",
  "description": "Schema for registering a consumer with the SISAS Consumer Registry",
  "type": "object",
  "required": ["consumer_id", "phase", "scopes", "capabilities", "signal_types"],
  "properties": {
    "consumer_id": {
      "type": "string",
      "pattern": "^phase_[0-9]{2}_consumer$",
      "description": "Unique consumer identifier following the pattern phase_XX_consumer"
    },
    "phase": {
      "type": "integer",
      "minimum": 0,
      "maximum": 9,
      "description": "Phase number this consumer processes (0-9)"
    },
    "scopes": {
      "type": "object",
      "description": "Scopes this consumer can process",
      "required": ["policy_areas", "dimensions", "clusters", "questions"],
      "properties": {
        "policy_areas": {
          "type": "array",
          "items": {"type": "string", "pattern": "^PA[0-9]{2}$"},
          "description": "List of policy area codes (PA01-PA10)"
        },
        "dimensions": {
          "type": "array",
          "items": {"type": "string", "pattern": "^D[1-6]$"},
          "description": "List of dimension codes (D1-D6)"
        },
        "clusters": {
          "type": "array",
          "items": {"type": "string", "pattern": "^CL[1-4]$"},
          "description": "List of cluster codes (CL1-CL4)"
        },
        "questions": {
          "type": "array",
          "items": {"type": "string", "pattern": "^Q[0-9]{3}$"},
          "description": "List of question codes (Q001-Q300)"
        }
      }
    },
    "capabilities": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "List of processing capabilities this consumer provides"
    },
    "signal_types": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "List of signal types this consumer can handle"
    },
    "config": {
      "type": "object",
      "description": "Optional consumer configuration",
      "properties": {
        "priority": {
          "type": "string",
          "enum": ["LOWEST", "LOW", "MEDIUM", "HIGH", "HIGHEST"],
          "default": "MEDIUM"
        },
        "max_concurrent": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "default": 4
        },
        "timeout_ms": {
          "type": "integer",
          "minimum": 1000,
          "maximum": 300000,
          "default": 30000
        },
        "retry_policy": {
          "type": "object",
          "properties": {
            "max_retries": {"type": "integer", "default": 3},
            "backoff_ms": {"type": "integer", "default": 1000},
            "backoff_multiplier": {"type": "number", "default": 2.0}
          }
        }
      }
    }
  }
}
```

---

## 5. Example Consumer Registration Code

### 5.1 Python Registration Example

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class Priority(Enum):
    LOWEST = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    HIGHEST = 5

@dataclass
class ConsumerScopes:
    policy_areas: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    clusters: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "policy_areas": self.policy_areas,
            "dimensions": self.dimensions,
            "clusters": self.clusters,
            "questions": self.questions
        }

@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff_ms: int = 1000
    backoff_multiplier: float = 2.0

@dataclass
class ConsumerConfig:
    priority: Priority = Priority.MEDIUM
    max_concurrent: int = 4
    timeout_ms: int = 30000
    retry_policy: Optional[RetryPolicy] = None

@dataclass
class ConsumerRegistration:
    consumer_id: str
    phase: int
    scopes: ConsumerScopes
    capabilities: List[str]
    signal_types: List[str]
    config: Optional[ConsumerConfig] = None

# Example: Register Phase 04 Consumer
def register_phase_04_consumer(registry: "ConsumerRegistry") -> str:
    """Register the Phase 04 Scoring Consumer."""
    
    scopes = ConsumerScopes(
        policy_areas=[f"PA{i:02d}" for i in range(1, 11)],
        dimensions=[f"D{i}" for i in range(1, 7)],
        clusters=[f"CL{i}" for i in range(1, 5)],
        questions=[f"Q{i:03d}" for i in range(1, 301)]
    )
    
    registration = ConsumerRegistration(
        consumer_id="phase_04_consumer",
        phase=4,
        scopes=scopes,
        capabilities=[
            "score_primary",
            "score_secondary", 
            "calculate_weights",
            "normalize_scores"
        ],
        signal_types=[
            "SCORING_PRIMARY",
            "SCORING_WEIGHTED",
            "SCORING_NORMALIZED"
        ],
        config=ConsumerConfig(
            priority=Priority.MEDIUM,
            max_concurrent=8,
            timeout_ms=45000,
            retry_policy=RetryPolicy(
                max_retries=3,
                backoff_ms=1000,
                backoff_multiplier=2.0
            )
        )
    )
    
    return registry.register(registration)

# Example: Bulk registration of all consumers
def register_all_consumers(registry: "ConsumerRegistry") -> List[str]:
    """Register all 10 phase consumers."""
    
    consumer_specs = [
        {
            "consumer_id": "phase_00_consumer",
            "phase": 0,
            "capabilities": ["extract_raw", "parse_input", "tokenize", "normalize"],
            "signal_types": ["EXTRACTION_RAW", "EXTRACTION_PARSED", "EXTRACTION_NORMALIZED"],
            "priority": Priority.HIGHEST,
            "max_concurrent": 10,
            "timeout_ms": 30000
        },
        {
            "consumer_id": "phase_01_consumer",
            "phase": 1,
            "capabilities": ["assemble_components", "merge_fragments", "structure_data", "validate_assembly"],
            "signal_types": ["ASSEMBLY_COMPONENT", "ASSEMBLY_MERGED", "ASSEMBLY_STRUCTURED"],
            "priority": Priority.HIGH,
            "max_concurrent": 8,
            "timeout_ms": 45000
        },
        # ... additional consumers follow same pattern
    ]
    
    registered_ids = []
    for spec in consumer_specs:
        scopes = ConsumerScopes(
            policy_areas=[f"PA{i:02d}" for i in range(1, 11)],
            dimensions=[f"D{i}" for i in range(1, 7)],
            clusters=[f"CL{i}" for i in range(1, 5)],
            questions=[f"Q{i:03d}" for i in range(1, 301)]
        )
        
        registration = ConsumerRegistration(
            consumer_id=spec["consumer_id"],
            phase=spec["phase"],
            scopes=scopes,
            capabilities=spec["capabilities"],
            signal_types=spec["signal_types"],
            config=ConsumerConfig(
                priority=spec.get("priority", Priority.MEDIUM),
                max_concurrent=spec.get("max_concurrent", 4),
                timeout_ms=spec.get("timeout_ms", 30000)
            )
        )
        
        consumer_id = registry.register(registration)
        registered_ids.append(consumer_id)
    
    return registered_ids
```

### 5.2 Consumer Registry Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class ConsumerRegistry(ABC):
    """Abstract base class for consumer registry implementations."""
    
    @abstractmethod
    def register(self, registration: ConsumerRegistration) -> str:
        """
        Register a new consumer.
        
        Args:
            registration: Consumer registration details
            
        Returns:
            Registered consumer ID
            
        Raises:
            ConsumerAlreadyExistsError: If consumer_id already registered
            InvalidRegistrationError: If registration data is invalid
        """
        pass
    
    @abstractmethod
    def deregister(self, consumer_id: str) -> bool:
        """
        Remove a consumer from the registry.
        
        Args:
            consumer_id: ID of consumer to remove
            
        Returns:
            True if consumer was removed, False if not found
        """
        pass
    
    @abstractmethod
    def get(self, consumer_id: str) -> Optional[ConsumerRegistration]:
        """
        Retrieve a consumer registration.
        
        Args:
            consumer_id: ID of consumer to retrieve
            
        Returns:
            Consumer registration or None if not found
        """
        pass
    
    @abstractmethod
    def find_by_signal_type(self, signal_type: str) -> List[ConsumerRegistration]:
        """
        Find all consumers capable of handling a signal type.
        
        Args:
            signal_type: Signal type to match
            
        Returns:
            List of capable consumer registrations
        """
        pass
    
    @abstractmethod
    def find_by_phase(self, phase: int) -> Optional[ConsumerRegistration]:
        """
        Find the consumer for a specific phase.
        
        Args:
            phase: Phase number (0-9)
            
        Returns:
            Consumer registration or None if not found
        """
        pass
    
    @abstractmethod
    def list_all(self) -> List[ConsumerRegistration]:
        """
        List all registered consumers.
        
        Returns:
            List of all consumer registrations
        """
        pass
```

---

## 6. Consumer Health Monitoring

### 6.1 Health Check Protocol

Each consumer MUST implement the health check endpoint:

```python
@dataclass
class HealthStatus:
    consumer_id: str
    status: str  # "HEALTHY", "DEGRADED", "UNHEALTHY"
    last_heartbeat: datetime
    signals_processed: int
    signals_failed: int
    average_latency_ms: float
    queue_depth: int
    error_rate: float

def health_check(consumer_id: str) -> HealthStatus:
    """Perform health check on consumer."""
    pass
```

### 6.2 Health Thresholds

| Metric | Healthy | Degraded | Unhealthy |
|--------|---------|----------|-----------|
| Error Rate | < 1% | 1-5% | > 5% |
| Latency (p99) | < 100ms | 100-500ms | > 500ms |
| Queue Depth | < 100 | 100-500 | > 500 |
| Heartbeat Age | < 30s | 30-60s | > 60s |

---

*End of Consumer Registry Specification*
