# ADR-005: Data Storage Strategy

**Status:** Accepted  
**Date:** 2024-01-15  
**Deciders:** Engineering Team

## Context

The system has multiple data storage needs:
1. Relational data: athletes, sessions, sets, recommendations
2. Time-series data: BPM readings, performance over time
3. Vector data: exercise embeddings for semantic similarity (future)
4. JSON/flexible: event payloads, feature contributions

## Decision

**PostgreSQL for MVP (all data types), defer specialized stores.**

Use a single PostgreSQL 15 instance with:
- JSONB columns for flexible/semi-structured data
- UUID primary keys throughout
- Proper indexes for performance
- TimescaleDB and vector DB deferred to Phase 2

## Alternatives Considered

### Option A: Multiple Databases from Start
- ✅ Purpose-built tools for each data type
- ❌ High operational complexity for MVP
- ❌ Data sync across stores
- ❌ Premature optimization

### Option B: NoSQL (MongoDB)
- ✅ Flexible schema
- ❌ Weaker consistency guarantees
- ❌ No ACID transactions
- ❌ Less suitable for relational workout data

### Option C: PostgreSQL Only (Chosen)
- ✅ JSONB for flexible data (event payloads, feature contributions)
- ✅ Full ACID compliance
- ✅ Excellent Python ecosystem (SQLAlchemy, psycopg2)
- ✅ Extensible (TimescaleDB extension available when needed)
- ✅ Single store = simple operations

## Schema Decisions

- `exercise_sets.bpm_avg/bpm_peak`: Store aggregates, not raw time-series (defer TimescaleDB)
- `effort_estimates.feature_contributions`: JSONB for explainability data
- `recommendations.cue_list/safety_reason_codes`: JSONB arrays

## Consequences

**Positive:**
- Single database to manage and backup
- Strong consistency for workout data
- JSONB allows schema evolution without migrations

**Negative:**
- Not optimized for time-series queries at scale
- No vector similarity search for exercise embeddings

**Upgrade Path:**
- Add TimescaleDB extension for time-series when BPM volume grows
- Add pgvector extension for exercise embeddings in Phase 3
- Consider read replicas when query load increases
