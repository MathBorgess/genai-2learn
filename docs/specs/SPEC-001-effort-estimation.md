# SPEC-001: Effort Estimation

**Version:** 1.0  
**Status:** Draft  
**Service:** effort-intelligence

## Overview

Given data from a completed exercise set, produce a normalized effort estimate that represents how hard the athlete worked (0–100 scale) and an estimated Reps-in-Reserve (RIR).

## Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| set_id | UUID | Yes | Reference to exercise_sets record |
| exercise_id | String | Yes | Exercise identifier |
| load_kg | Float | Yes | Load used in kilograms |
| reps | Integer | Yes | Reps completed |
| rir_reported | Float | No | Self-reported RIR (0-10) |
| rpe_reported | Float | No | Self-reported RPE (1-10) |
| bpm_avg | Float | No | Average heart rate |
| bpm_peak | Float | No | Peak heart rate |
| history | Array | No | Previous sets for context |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| effort_score | Float | Normalized effort 0-100 |
| rir_estimate | Float | Estimated reps in reserve |
| confidence | Float | Confidence in estimate (0-1) |
| feature_contributions | Object | Which signals drove the estimate |

## Algorithm (MVP Rule-Based)

### Signal Priority
1. `rir_reported` (highest priority — direct athlete feedback)
2. `rpe_reported` (secondary — RPE to RIR conversion)
3. `rep_ratio` (reps / expected_max_reps)
4. `bpm_avg` (never used as sole signal)

### Effort Score Calculation

```python
# When rir_reported is available (most reliable)
effort_score = (10 - rir_reported) * 10
rir_estimate = rir_reported

# When only rpe_reported is available
rir_estimate = 10 - rpe_reported
effort_score = rpe_reported * 10

# When neither is available (rep_ratio method)
rep_ratio = reps / expected_max_reps  # default 12 if unknown
effort_score = min(rep_ratio * 75, 95)  # cap at 95
rir_estimate = max((1 - rep_ratio) * 5, 0)
```

### Confidence Calculation

| Condition | Confidence Modifier |
|-----------|--------------------:|
| rir_reported present | +0.4 |
| rpe_reported present | +0.3 |
| bpm_avg present | +0.2 |
| data_quality_score | × data_quality_score |

## Acceptance Criteria

1. **AC-001**: When `rir_reported=2`, effort_score MUST be 80
2. **AC-002**: When `rir_reported=0`, effort_score MUST be 100
3. **AC-003**: Confidence MUST be between 0.0 and 1.0 (inclusive)
4. **AC-004**: `feature_contributions` MUST indicate which signals were used
5. **AC-005**: MAE ≤ 1.5 RIR on benchmark test set (Phase 2 with ML)
6. **AC-006**: Processing time ≤ 100ms per estimate

## Test Scenarios

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| S1: Full data | reps=8, load=100, rir=2 | effort=80, conf≥0.7 |
| S2: Only reps | reps=10, load=80 | effort estimated from ratio |
| S3: Missing fields | load only | data_quality_score < 0.5 |
| S4: Max effort | rir=0 | effort=100 |
| S5: Low effort | rir=8 | effort=20 |
