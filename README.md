# Vectrion

**Vectrion** is a production-grade Retrieval-Augmented Generation (RAG) backend designed for reliability, scalability, and operational clarity.

It provides asynchronous document ingestion, structured chunk persistence, vector indexing, guardrails, and observability using industry-standard infrastructure components.

Vectrion is built with an architecture-first mindset — prioritizing fault tolerance, idempotency, and system transparency over demo-level implementations.

---

## Overview

Modern GenAI systems require more than vector search and prompt templates.  
Vectrion implements a full RAG backend lifecycle:

- Admin-driven document ingestion
- Async processing pipeline
- Chunk persistence for re-embedding
- Vector indexing in Qdrant
- Guardrail-enforced generation
- Conversation logging
- Retry & Dead Letter Queue support
- Production-ready observability hooks

---

## Architecture

Vectrion follows a layered, fault-isolated architecture:

**Edge Layer**
- Load Balancer
- API Gateway
- Rate limiting
- Authentication

**Async Ingestion**
- RabbitMQ
- Celery Workers
- Retry with exponential backoff
- Dead Letter Queue support

**Storage Layer**
- PostgreSQL (metadata, chunks, conversations)
- Qdrant (vector storage)
- S3 / object storage (documents)

**Query Pipeline**
- Vector retrieval (Top-K)
- Context assembly
- Prompt construction
- Guardrails (input + output validation)
- LLM invocation
- Response logging

**Observability**
- Flower (worker monitoring)
- Prometheus metrics
- Grafana dashboards
- Jaeger tracing

---

## Key Design Principles

### 1. Async First
Heavy operations such as extraction, chunking, and embedding run in background workers to prevent API blocking.

### 2. Idempotent Ingestion
Retries do not create duplicate chunks or embeddings.

### 3. Chunk Persistence
Chunks are stored in PostgreSQL to enable:
- Re-embedding with new models
- Auditability
- Debugging retrieval quality

### 4. Guardrails
Vectrion enforces:
- Input validation (prompt injection prevention)
- System-level constraints
- Output moderation

### 5. Failure Isolation
Each stage of ingestion is separated into tasks:
- Document processing
- Embedding & indexing

Failures are retried automatically and escalated to DLQ when needed.

### 6. Observability by Design
Metrics and tracing hooks are built into:
- API requests
- Celery tasks
- Vector operations
- LLM calls

---

## Features

- Admin document upload
- Async PDF processing
- Chunk extraction & persistence
- Embedding generation
- Qdrant vector indexing
- Top-K semantic retrieval
- Multi-turn memory support
- Input & output guardrails
- Conversation storage
- Retry logic with DLQ
- Redis-based rate limiting
- Prometheus-ready metrics
- Production-friendly architecture

---

## Tech Stack

- FastAPI
- Celery
- RabbitMQ
- PostgreSQL
- Qdrant
- Redis
- OpenAI (or compatible LLM provider)
- Prometheus
- Grafana
- Jaeger

---

## Production Considerations

Vectrion is designed with production constraints in mind:

- Idempotent task execution
- Safe retries
- Vector consistency guarantees
- Structured logging
- Token usage tracking
- Quota enforcement
- Backup strategy for PostgreSQL and Qdrant
- Environment-based secret management

