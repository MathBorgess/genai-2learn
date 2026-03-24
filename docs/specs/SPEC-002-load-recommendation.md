# SPEC-002: Load Recommendation

**Version:** 1.0  
**Status:** Draft  
**Service:** effort-intelligence

## Overview

Given an effort estimate and set context, issue a load recommendation for the athlete's next set of the same exercise. Prioritize safety over performance optimization.

## Inputs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| effort_score | Float | Yes | From effort estimation (0-100) |
| confidence | Float | Yes | Confidence in estimate (0-1) |
| rir_estimate | Float | Yes | Estimated reps in reserve |
| pain_flag | Boolean | No | Athlete reports pain |
| current_load_kg | Float | Yes | Current set load |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| action_type | Enum | INCREASE_LOAD, DECREASE_LOAD, MAINTAIN, ADJUST_TECHNIQUE |
| load_delta_pct | Float | % change in load (-20 to +10) |
| cue_list | Array | Technique cues to provide |
| safety_reason_codes | Array | Safety rules triggered |
| rationale | String | Human-readable explanation |

## Decision Logic

### Safety Rules (Highest Priority — Always Apply)

| Rule | Condition | Action |
|------|-----------|--------|
| SAFETY-001 | pain_flag == true | DECREASE_LOAD (-10%) |
| SAFETY-002 | effort_score > 95 | DECREASE_LOAD or MAINTAIN |
| SAFETY-003 | confidence < 0.4 | MAINTAIN (conservative) |

### Confidence Tiers

| Tier | Confidence Range | Allowed Actions |
|------|-----------------|-----------------|
| HIGH | ≥ 0.7 | All actions |
| MEDIUM | 0.4 – 0.7 | MAINTAIN, ADJUST_TECHNIQUE, minor DECREASE_LOAD |
| LOW | < 0.4 | MAINTAIN only |

### Recommendation Rules (Apply After Safety Check)

| Condition | Action | load_delta_pct |
|-----------|--------|----------------|
| effort < 40 AND confidence ≥ 0.7 | INCREASE_LOAD | +5% |
| effort 40-60 AND confidence ≥ 0.7 | INCREASE_LOAD | +2.5% |
| effort 60-80 | MAINTAIN | 0% |
| effort 80-95 AND confidence ≥ 0.7 | DECREASE_LOAD | -5% |
| effort > 95 | DECREASE_LOAD | -10% |

### CRITICAL: Never Increase Load Rules

The system MUST NEVER recommend INCREASE_LOAD when:
1. `confidence < 0.7`
2. `pain_flag == true`
3. `effort_score > 95`

## Acceptance Criteria

1. **AC-001**: NEVER output INCREASE_LOAD when confidence < 0.7
2. **AC-002**: ALWAYS output DECREASE_LOAD when pain_flag is true
3. **AC-003**: `safety_reason_codes` MUST be populated when safety rules trigger
4. **AC-004**: `rationale` MUST be human-readable (non-technical)
5. **AC-005**: `load_delta_pct` MUST be 0 when action_type is MAINTAIN
6. **AC-006**: Processing time ≤ 50ms per recommendation

## Test Scenarios

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| S1: High confidence, low effort | effort=35, conf=0.8 | INCREASE_LOAD |
| S2: Low confidence | effort=35, conf=0.3 | MAINTAIN |
| S3: Pain flag | pain=true, effort=60 | DECREASE_LOAD |
| S4: Max effort | effort=98, conf=0.9 | DECREASE_LOAD |
| S5: Normal effort | effort=70, conf=0.8 | MAINTAIN |
