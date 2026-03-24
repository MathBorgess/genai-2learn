# Safety Guardrails Policy

## Purpose
These guardrails are non-negotiable safety constraints that override ALL other recommendation logic.

## Hard Rules (Cannot Be Overridden)

### GUARDRAIL-001: Pain Signal
**Condition:** `pain_flag == true`  
**Action:** ALWAYS recommend DECREASE_LOAD  
**load_delta_pct:** -10% minimum  
**safety_reason_code:** `PAIN_FLAG_ACTIVE`  
**Rationale template:** "Pain was reported. Load has been reduced for safety. Please consult a professional if pain persists."

### GUARDRAIL-002: Maximum Effort
**Condition:** `effort_score > 95`  
**Action:** DECREASE_LOAD or MAINTAIN (never INCREASE_LOAD)  
**safety_reason_code:** `MAX_EFFORT_THRESHOLD`  
**Rationale template:** "Your effort level was at or near maximum. Continuing at this intensity risks injury."

### GUARDRAIL-003: Low Confidence
**Condition:** `confidence < 0.4`  
**Action:** MAINTAIN only  
**safety_reason_code:** `LOW_CONFIDENCE_FALLBACK`  
**Rationale template:** "Insufficient data to make a confident recommendation. Maintaining current load as a precaution."

### GUARDRAIL-004: Data Quality
**Condition:** `data_quality_score < 0.3`  
**Action:** Return conservative fallback (MAINTAIN)  
**safety_reason_code:** `DATA_QUALITY_INSUFFICIENT`  
**Rationale template:** "Set data quality is too low for reliable analysis. Please ensure all required fields are recorded."

## Soft Rules (Can Be Overridden by High Confidence)

### GUARDRAIL-005: Consecutive High Effort
**Condition:** 3+ consecutive sets with effort > 80%  
**Action:** Recommend REST or session review  
**safety_reason_code:** `CONSECUTIVE_HIGH_EFFORT`

## Audit Requirements
All triggered guardrails MUST be logged with:
- `safety_reason_codes` in the recommendation output
- Timestamp of trigger
- Which rule was applied
