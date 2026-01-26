# Phase 3 RUNBOOK - SOTA Operations Guide

## Quick Reference

**Version**: 2.0.0-SOTA  
**Phase**: Scoring Transformation with ML Enhancement  
**Criticality**: CRITICAL  
**Contact**: F.A.R.F.A.N Core Team - SOTA Division

---

## Table of Contents

1. [Overview](#overview)
2. [SOTA Components](#sota-components)
3. [Configuration](#configuration)
4. [Operations](#operations)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tuning](#performance-tuning)
8. [Incident Response](#incident-response)

---

## Overview

### Mission

Transform Phase 2 evidence outputs into normalized quantitative scores using hybrid deterministic + ML approach.

### Architecture

```
Phase 2 Evidence → Phase 3 Scoring → Phase 4 Aggregation
                      ↓
                  SOTA ML Enhancement
                   ├─ Bayesian Inference
                   ├─ Attention Mechanisms
                   ├─ Online Learning
                   ├─ Kalman Filtering
                   └─ Probabilistic Models
```

### Key Metrics

- **Throughput**: 10,000 questions/second
- **Latency**: <10ms p99 (deterministic), <50ms p99 (with ML)
- **Accuracy**: 96/96 adversarial tests passing
- **ML Convergence**: 50-1000 observations depending on component

---

## SOTA Components

### 1. BayesianConfidenceEstimator

**Purpose**: Adaptive confidence weight estimation

**Configuration**:
```python
scorer = SOTASignalEnrichedScorer(
    enable_bayesian_inference=True,  # Enable Bayesian learning
)
```

**Operational Parameters**:
- `prior_alpha`: Success prior (default: 2.0)
- `prior_beta`: Failure prior (default: 2.0)
- Convergence: ~100 observations for stable estimates

**Monitoring**:
- Track `observation_count` for convergence progress
- Monitor posterior means vs fixed weights
- Check credible intervals for uncertainty

**Tuning**:
- Increase priors (α, β) for stronger regularization
- Decrease priors for faster adaptation to new data

### 2. AttentionPatternDetector

**Purpose**: Dynamic signal pattern discovery

**Configuration**:
```python
scorer = SOTASignalEnrichedScorer(
    enable_attention_patterns=True,  # Enable attention-based patterns
)
```

**Operational Parameters**:
- `d_model`: Embedding dimension (default: 64)
- `num_heads`: Number of attention heads (default: 4)
- Convergence: ~1000 signal pairs

**Monitoring**:
- Track attention scores for interpretability
- Monitor discovered patterns vs hardcoded rules
- Check pattern strength distribution

**Tuning**:
- Increase `d_model` for more expressive embeddings
- Add more `num_heads` for diverse pattern types
- Reduce if memory/compute constrained

### 3. OnlineThresholdLearner

**Purpose**: Continuous threshold optimization

**Configuration**:
```python
scorer = SOTASignalEnrichedScorer(
    enable_online_learning=True,  # Enable threshold learning
)
```

**Operational Parameters**:
- `learning_rate`: Step size (default: 0.01)
- `momentum`: Velocity coefficient (default: 0.9)
- Convergence: ~50-100 examples per threshold

**Monitoring**:
- Track threshold drift over time
- Monitor update_count for convergence
- Check velocities for stability

**Tuning**:
- Decrease learning_rate if thresholds oscillate
- Increase momentum for smoother updates
- Reset if distribution shift detected

### 4. KalmanSignalFilter

**Purpose**: Optimal temporal signal tracking

**Configuration**:
```python
# Per-signal Kalman filters automatically created
# No explicit configuration needed
```

**Operational Parameters**:
- `Q`: Process noise (default: 0.01)
- `R`: Measurement noise (default: 0.1)
- Convergence: Immediate (optimal estimator)

**Monitoring**:
- Track error covariance (P) for uncertainty
- Monitor freshness estimates vs simple decay
- Check Kalman gain for filter behavior

**Tuning**:
- Increase `Q` if signal changes rapidly
- Decrease `R` if measurements reliable
- Adjust based on observed noise characteristics

### 5. Probabilistic Quality Cascade

**Purpose**: Uncertainty-aware quality resolution

**Configuration**:
```python
# Integrated into SOTASignalEnrichedScorer
# Always active when SOTA enabled
```

**Operational Parameters**:
- Prior probabilities over quality levels
- Likelihood functions for score/completeness
- Evidence strength weighting

**Monitoring**:
- Track quality distribution entropy
- Monitor promotion/demotion confidence
- Check posterior probabilities

**Tuning**:
- Adjust likelihood functions based on data
- Tune evidence weights for sensitivity
- Balance deterministic fallback vs probabilistic

---

## Configuration

### Deployment Modes

#### 1. Production (Conservative)
```python
scorer = SOTASignalEnrichedScorer(
    signal_registry=registry,
    enable_threshold_adjustment=True,
    enable_quality_validation=True,
    enable_online_learning=False,        # Disable learning in prod
    enable_bayesian_inference=True,      # Use learned weights (no updates)
    enable_attention_patterns=False,     # Use validated patterns only
)
```

**Rationale**: Stability over adaptation. Use pre-trained ML components without online updates.

#### 2. Learning (Continuous Improvement)
```python
scorer = SOTASignalEnrichedScorer(
    signal_registry=registry,
    enable_threshold_adjustment=True,
    enable_quality_validation=True,
    enable_online_learning=True,         # Learn continuously
    enable_bayesian_inference=True,      # Update posteriors
    enable_attention_patterns=True,      # Discover new patterns
)
```

**Rationale**: Adaptation over stability. Continuously improve from production data.

#### 3. Legacy (Backward Compatible)
```python
scorer = SignalEnrichedScorer(  # Legacy alias
    signal_registry=registry,
    enable_threshold_adjustment=True,
    enable_quality_validation=True,
)
```

**Rationale**: No ML, deterministic behavior only. For regression testing.

### Environment Variables

```bash
# SOTA Feature Flags
export PHASE3_ENABLE_BAYESIAN=true
export PHASE3_ENABLE_ATTENTION=true
export PHASE3_ENABLE_ONLINE_LEARNING=false  # Disable in prod

# Performance Tuning
export PHASE3_ATTENTION_DIM=64
export PHASE3_ATTENTION_HEADS=4
export PHASE3_LEARNING_RATE=0.01

# Monitoring
export PHASE3_LOG_LEVEL=INFO
export PHASE3_METRICS_ENABLED=true
```

---

## Operations

### Startup Checklist

- [ ] Verify Python environment (3.10+)
- [ ] Check required packages: numpy, scipy (optional)
- [ ] Load pre-trained ML models (if any)
- [ ] Initialize signal registry
- [ ] Validate configuration
- [ ] Run health checks
- [ ] Enable metrics collection

### Health Checks

```python
# Check SOTA components initialized
assert scorer.bayesian_estimator is not None
assert scorer.attention_detector is not None
assert scorer.threshold_learner is not None

# Check ML convergence status
bayesian_obs = scorer.bayesian_estimator.observation_count
assert bayesian_obs >= 100, "Bayesian estimator needs more data"

# Check threshold stability
learner_stats = scorer.threshold_learner.get_learning_stats()
assert learner_stats["update_count"] >= 50, "Thresholds need more updates"
```

### Routine Maintenance

#### Daily
- Monitor ML convergence metrics
- Check threshold drift (should be < 0.01/day after convergence)
- Verify attention pattern stability
- Review quality cascade decisions

#### Weekly
- Analyze Bayesian credible intervals (should narrow over time)
- Audit discovered attention patterns
- Validate online learning performance vs baseline
- Backup ML model state

#### Monthly
- Comprehensive performance review
- A/B test SOTA vs legacy approach
- Tune hyperparameters if needed
- Update documentation with learnings

---

## Monitoring

### Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Bayesian Observation Count | >100 | <50 |
| Attention Pattern Count | 3-10 | <2 or >20 |
| Threshold Update Rate | <10/hour | >100/hour |
| Kalman Uncertainty (avg) | <0.1 | >0.3 |
| Quality Entropy (avg) | 0.5-1.5 bits | >2.0 bits |

### Logging

```python
logger.info(
    "SOTA scoring completed",
    question_id=question_id,
    bayesian_weight=weight,
    attention_patterns=len(patterns),
    threshold_adjusted=adjusted_threshold,
    kalman_estimate=freshness,
    quality_distribution=quality_probs
)
```

### Dashboards

1. **ML Convergence Dashboard**
   - Bayesian posterior evolution
   - Threshold learning curves
   - Attention pattern discovery rate

2. **Performance Dashboard**
   - Latency (deterministic vs ML)
   - Throughput degradation with ML
   - Memory/CPU utilization

3. **Quality Dashboard**
   - Quality distribution shifts
   - Promotion/demotion rates
   - Cascade resolution confidence

---

## Troubleshooting

### Issue: Bayesian Weights Diverging

**Symptoms**: Confidence weights drift far from reasonable values (e.g., >0.99 or <0.01)

**Diagnosis**:
```python
for conf, params in scorer.bayesian_estimator.posteriors.items():
    print(f"{conf}: α={params['alpha']}, β={params['beta']}")
```

**Solutions**:
1. Check data quality - are outcomes labeled correctly?
2. Increase priors (α, β) for stronger regularization
3. Reset posteriors if distribution shift detected
4. Consider using running window of recent observations

### Issue: Attention Patterns Unstable

**Symptoms**: Discovered patterns change frequently, attention scores fluctuate

**Diagnosis**:
```python
patterns = scorer.attention_detector.detect_patterns(signals)
print(f"Pattern count: {len(patterns)}")
for p in patterns:
    print(f"Strength: {p['pattern_strength']}")
```

**Solutions**:
1. Increase attention threshold to reduce noise
2. Use larger `d_model` for more stable embeddings
3. Add temporal smoothing to attention scores
4. Pre-train on larger dataset before deployment

### Issue: Thresholds Not Converging

**Symptoms**: Thresholds oscillate, update_count high but no convergence

**Diagnosis**:
```python
stats = scorer.threshold_learner.get_learning_stats()
print(f"Updates: {stats['update_count']}")
print(f"Thresholds: {stats['current_thresholds']}")
print(f"Velocities: {stats['velocities']}")
```

**Solutions**:
1. Decrease learning_rate (try 0.001)
2. Increase momentum (try 0.95)
3. Check for label noise in training data
4. Use gradient clipping if gradients explode

### Issue: Kalman Filter Diverging

**Symptoms**: Freshness estimates become negative or >1.0, uncertainty grows unbounded

**Diagnosis**:
```python
estimate, uncertainty = kalman_filter.get_estimate_with_uncertainty()
print(f"Estimate: {estimate}, Uncertainty: {uncertainty}")
```

**Solutions**:
1. Clamp estimates to [0, 1] interval
2. Reduce process noise (Q)
3. Check measurement validity before updates
4. Reset filter if P > 10.0 (divergence indicator)

### Issue: Quality Cascade High Entropy

**Symptoms**: Quality decisions have high uncertainty (entropy >2 bits)

**Diagnosis**:
```python
entropy = quality_dist.entropy()
print(f"Decision entropy: {entropy:.2f} bits")
print(f"Probabilities: {quality_dist.probabilities}")
```

**Solutions**:
1. Strengthen evidence likelihood functions
2. Add more informative signals
3. Use deterministic fallback when entropy >threshold
4. Collect more training data for better priors

---

## Performance Tuning

### Latency Optimization

**Baseline**: 8ms p99 (deterministic only)
**With ML**: 45ms p99 (all SOTA enabled)

**Optimization Strategies**:

1. **Selective ML** - Only enable for complex questions
```python
if question_complexity > threshold:
    # Use full SOTA
    enable_all_sota = True
else:
    # Use deterministic only
    enable_all_sota = False
```

2. **Caching** - Cache ML computations for identical inputs
```python
@lru_cache(maxsize=1000)
def compute_attention_scores(signal_tuple):
    # Expensive attention computation
    pass
```

3. **Batch Processing** - Process multiple questions together
```python
# Vectorize Bayesian updates
weights = vectorized_bayesian_estimate(confidences)
```

4. **Lazy Evaluation** - Only compute when needed
```python
if not use_advanced_patterns:
    # Skip attention computation
    return simple_patterns
```

### Memory Optimization

**Baseline**: 2KB per question
**With ML**: 5KB per question

**Optimization Strategies**:

1. **Shared Components** - Reuse ML components across questions
2. **Pruning** - Remove low-attention patterns periodically
3. **Compression** - Quantize attention weights (float32 → float16)
4. **GC** - Explicitly delete temporary ML objects

---

## Incident Response

### P0: ML Component Failure

**Impact**: All SOTA scoring fails, fallback to deterministic

**Response**:
1. Disable all SOTA features immediately
2. Verify deterministic path working
3. Investigate ML failure (logs, state)
4. Restore from last known good model
5. Gradual re-enable with monitoring

### P1: Degraded ML Performance

**Impact**: ML provides poor scores, quality degraded

**Response**:
1. Compare ML vs deterministic on sample
2. Check for distribution shift (stats tests)
3. Consider model retraining
4. Increase monitoring granularity
5. A/B test fix before full rollout

### P2: Slow ML Convergence

**Impact**: ML not learning effectively

**Response**:
1. Check data quality and quantity
2. Verify hyperparameters reasonable
3. Add more informative features
4. Consider warm-start from similar domain
5. Extend convergence monitoring

---

## References

- **Phase 3 README**: Core architecture and theory
- **SOTA_FRONTIER_ENHANCEMENTS.md**: Detailed ML techniques
- **phase3_24_00_signal_enriched_scoring.py**: Implementation
- **phase3_00_00_sota_primitives.py**: ML primitives

## Contact

- **Technical Lead**: F.A.R.F.A.N Core Team - SOTA Division
- **On-call**: [PagerDuty integration]
- **Slack**: #phase3-sota-ops
- **Email**: sota@farfan-pipeline.org

---

**Last Updated**: 2026-01-26  
**Version**: 2.0.0-SOTA  
**Next Review**: 2026-02-26
