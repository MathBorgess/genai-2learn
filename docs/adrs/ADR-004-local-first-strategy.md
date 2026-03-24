# ADR-004: Local-First Development Strategy

**Status:** Accepted  
**Date:** 2024-01-15  
**Deciders:** Engineering Team

## Context

We need to validate the AI system and its architecture before investing in cloud infrastructure. The team needs to:
- Run the full system locally
- Iterate quickly on AI pipeline logic
- Run integration tests without cloud dependencies
- Keep infrastructure costs at zero during MVP

## Decision

**Docker Compose for all local development and testing.**

All services, databases, and message brokers run in Docker Compose locally. Cloud deployment is deferred until after MVP validation.

## Alternatives Considered

### Option A: Cloud-First (AWS/GCP from day one)
- ✅ Production-like environment
- ❌ Cost during development/validation
- ❌ Slow iteration (deploy cycles)
- ❌ Network dependency

### Option B: Kubernetes Local (minikube/kind)
- ✅ Closer to production K8s
- ❌ High resource usage on developer machines
- ❌ Complex setup and maintenance
- ❌ Overkill for 4 services

### Option C: Docker Compose (Chosen)
- ✅ Simple, fast, zero cost
- ✅ `docker-compose up` gets full system running
- ✅ Easy to share dev environment via docker-compose.yml
- ✅ Supports healthchecks and service dependencies

## Consequences

**Positive:**
- Any developer can run the full system with one command
- Fast iteration: code change → rebuild → test in seconds
- No cloud costs during MVP validation
- `docker-compose.dev.yml` enables hot reload

**Negative:**
- Local environment may differ from production
- No load testing at scale locally

**Future:**
- Add Kubernetes manifests when ready to deploy
- Consider Terraform for cloud infrastructure
