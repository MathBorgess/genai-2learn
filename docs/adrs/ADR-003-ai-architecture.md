# ADR-003: AI Pipeline Architecture

**Status:** Accepted  
**Date:** 2024-01-15  
**Deciders:** Engineering Team

## Context

The core AI capability is effort estimation and load recommendation. We need to decide how to implement the intelligence:
- Effort estimation: given set data (reps, load, RIR, BPM), estimate actual effort (0-100)
- Load recommendation: given effort estimate, recommend next set adjustment

Key constraints:
- MVP needs to ship quickly
- Training data is not yet available
- Safety is paramount (never recommend dangerous loads)
- System must be auditable and explainable
- Must work without external AI API calls (local-first)

## Decision

**Rule-based hybrid first, ML-ready architecture.**

Implement a multi-agent pipeline with rule-based logic for MVP:
1. `ValidationAgent`: validates data quality, flags issues
2. `EffortAgent`: estimates effort using physiological rules
3. `RecommendationAgent`: applies policy-based recommendations with guardrails

Architecture is ML-ready: swap rule-based implementations with trained models without changing the pipeline interface.

## Alternatives Considered

### Option A: Pure Machine Learning
- ✅ Potentially more accurate
- ❌ No training data yet
- ❌ Black box, not auditable
- ❌ Requires data collection phase first
- ❌ Cannot ship MVP quickly

### Option B: Pure LLM (GPT-4, Claude)
- ✅ Quick to prototype
- ❌ Expensive, not local-first
- ❌ Non-deterministic outputs
- ❌ Safety not guaranteed
- ❌ Latency too high for real-time recommendations

### Option C: Rule-Based Only
- ✅ Simple, fast, auditable
- ❌ Cannot improve over time
- ❌ Cannot handle edge cases well
- ❌ Brittle with new exercises

### Option D: Rule-Based Hybrid (Chosen)
- ✅ Ships now with zero training data
- ✅ Fully auditable and explainable
- ✅ Safety rules are explicit and testable
- ✅ Architecture allows seamless ML upgrade path
- ✅ Confidence scores gate recommendations safely

## Agent Pipeline Design

```
SetRecorded → ValidationAgent → EffortAgent → RecommendationAgent → RecommendationIssued
```

### Safety Guardrails (Non-negotiable)
1. **Never** recommend INCREASE_LOAD when confidence < 0.7
2. **Always** recommend DECREASE_LOAD when pain_flag is true
3. Conservative fallback when data quality < 0.3

## Consequences

**Positive:**
- System is safe and auditable from day one
- Can collect labeled data from user feedback for future ML training
- Each agent can be upgraded independently (ValidationAgent → ML-based, etc.)
- Confidence tiers prevent unsafe recommendations

**Negative:**
- Rule-based logic requires domain expertise to encode
- Will not generalize as well as ML for edge cases
- Needs ongoing rule maintenance as new exercises added

**Upgrade Path:**
- Phase 2: Train EffortAgent model on collected labeled data
- Phase 3: Fine-tune LLM for RecommendationAgent with safety constraints
- Phase 4: Add personalization (per-athlete models)
