# Vectrion Architecture

## Overview

Vectrion is designed as a production-ready RAG platform with:

- Event-driven document ingestion
- Multi-mode query execution (Chat + RAG)
- Semantic caching
- Rate limiting and quota control
- Usage tracking
- Scalable worker architecture

---

## Diagram Index

1. Container Architecture – System-level component view

![alt text](container_architecture.png)

2. Document Processing Flow – Async ingestion pipeline

![alt text](data_processing_flow.png)

3. Query Runtime Flow – Chat/RAG execution logic

![alt text](query_runtime_flow.png)