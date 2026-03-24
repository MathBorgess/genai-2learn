# ADR-001: Monolith vs Microservices Architecture

**Status:** Accepted  
**Date:** 2024-01-15  
**Deciders:** Engineering Team

## Context

We are building a new AI-powered fitness coaching system from scratch. We need to decide the initial architectural style. The system will:
- Handle real-time workout tracking
- Run an AI pipeline for effort estimation
- Issue load recommendations
- Eventually scale to many concurrent users

Key constraints:
- Small initial team (2-3 engineers)
- Need to iterate quickly to validate AI/ML concepts
- AI pipeline logic will evolve significantly
- Local development must be frictionless

## Decision

**Start with focused microservices (4 services) but NOT full decomposition.**

We chose a "focused microservices" approach:
- `api-gateway`: BFF for clients
- `workout-command`: domain logic for recording workouts
- `effort-intelligence`: AI pipeline (estimation + recommendation)
- `worker`: async event consumer

This gives us service isolation for the AI component (so it can evolve independently) without premature decomposition.

## Alternatives Considered

### Option A: Monolith First
- ✅ Fastest initial development
- ✅ Simplest deployment
- ❌ AI pipeline tightly coupled to domain logic
- ❌ Hard to scale AI processing independently
- ❌ Violates clean separation for AI/ML iteration

### Option B: Full Microservices (10+ services)
- ✅ Maximum flexibility
- ❌ Too much operational overhead for MVP
- ❌ Premature optimization
- ❌ Slows validation of AI/ML hypotheses

### Option C: Focused Microservices (Chosen)
- ✅ AI pipeline isolated for independent evolution
- ✅ Manageable complexity (4 services)
- ✅ Clear domain boundaries
- ✅ Can evolve to full decomposition later

## Consequences

**Positive:**
- AI/ML team can iterate on `effort-intelligence` without affecting workout recording
- Async processing via events keeps services decoupled
- Each service deployable and scalable independently

**Negative:**
- More complexity than monolith for initial development
- Distributed system challenges (eventual consistency, network failures)
- Need to manage inter-service communication

**Risks:**
- Over-engineering for current team size → mitigated by keeping services minimal
