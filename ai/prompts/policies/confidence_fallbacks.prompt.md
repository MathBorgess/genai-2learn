# Confidence Fallback Policy

## Purpose
Define behavior when the system has insufficient confidence to make optimal recommendations.

## Confidence Tiers

### HIGH Confidence (≥ 0.7)
**Data requirements met:** RIR or RPE reported + plausible data  
**Behavior:** Full recommendation logic applies  
**Allowed actions:** INCREASE_LOAD, DECREASE_LOAD, MAINTAIN, ADJUST_TECHNIQUE  

### MEDIUM Confidence (0.4 – 0.69)
**Data requirements met:** Some signals present but incomplete  
**Behavior:** Conservative recommendation logic  
**Allowed actions:** MAINTAIN, DECREASE_LOAD, ADJUST_TECHNIQUE  
**Note:** Never INCREASE_LOAD in medium confidence tier

### LOW Confidence (< 0.4)
**Data requirements:** Missing critical signals  
**Behavior:** Always return MAINTAIN  
**Allowed actions:** MAINTAIN only  
**Note:** Provide user with guidance on what data to collect next time

## Fallback Messaging Templates

### Low Confidence Message
> "We don't have enough data to make a confident recommendation for this set. 
> To improve recommendations, please report your Reps in Reserve (RIR) after each set."

### Medium Confidence Message
> "Based on available data, we recommend maintaining your current load. 
> Adding RIR or RPE data will enable more precise recommendations."

### Data Missing Message
> "This set is missing [field]. Future sets with complete data will receive 
> more accurate effort estimates."

## Confidence Score Composition

```
confidence = base_confidence × data_quality_score

base_confidence:
  + 0.4 if rir_reported present
  + 0.3 if rpe_reported present  
  + 0.2 if bpm_avg present
  + 0.1 baseline (always)
  = max 1.0
```
