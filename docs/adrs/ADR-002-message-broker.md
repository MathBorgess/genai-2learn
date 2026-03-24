# ADR-002: Message Broker Selection

**Status:** Accepted  
**Date:** 2024-01-15  
**Deciders:** Engineering Team

## Context

Services need to communicate asynchronously. When a set is recorded (`set.recorded`), the effort estimation pipeline should process it without blocking the workout recording flow. We need a message broker that:
- Supports pub/sub patterns
- Has dead letter queue support for error handling
- Is easy to run locally
- Has good Python library support
- Supports topic-based routing

## Decision

**Use RabbitMQ with topic exchange and an outbox-like pattern.**

Configuration:
- Exchange: `genai2learn` (topic type)
- Queues with routing keys: `set.recorded`, `effort.estimated`, `recommendation.issued`
- Dead Letter Queue: `set.recorded.dlq` for failed messages
- Python client: `pika`

## Alternatives Considered

### Option A: Apache Kafka
- ✅ High throughput, event sourcing, replay
- ❌ Overkill for MVP volumes
- ❌ Complex local setup (Zookeeper/KRaft)
- ❌ Higher operational complexity
- ❌ Steep learning curve

### Option B: Redis Pub/Sub
- ✅ Simple, fast
- ❌ No message persistence (fire and forget)
- ❌ No dead letter queue support
- ❌ Not suitable for reliable event processing

### Option C: Direct HTTP Calls
- ✅ Simplest to implement
- ❌ Tight coupling between services
- ❌ Synchronous processing blocks workout recording
- ❌ No retry or failure handling

### Option D: RabbitMQ (Chosen)
- ✅ Mature, reliable message broker
- ✅ Built-in DLQ support
- ✅ Topic routing for flexible event patterns
- ✅ Easy local Docker setup
- ✅ Good `pika` Python library

## Event Contract

```json
{
  "event_type": "set.recorded",
  "version": "1",
  "correlation_id": "uuid4",
  "causation_id": "uuid4",
  "timestamp": "2024-01-15T10:30:00Z",
  "payload": { ... }
}
```

## Consequences

**Positive:**
- Services are decoupled; workout recording never waits for AI processing
- Failed messages go to DLQ for investigation and replay
- Easy to add new consumers without modifying producers
- Topic routing allows fine-grained subscriptions

**Negative:**
- Eventual consistency: estimates available after async processing delay
- Need to handle message deduplication (idempotent consumers)
- Additional infrastructure component to manage

**Mitigation:**
- Poll endpoints (`GET /estimates/{set_id}`) for clients that need results
- Correlation IDs for tracing events across services
