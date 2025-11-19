# Ticket Triage Agent

(README generated)


---

## 🏭 Production Considerations (detailed)

This project is designed for demonstration and can be hardened for production. Below are concrete, actionable items and configurations to deploy, operate, and scale the service in production.

### 1) Containerization & Deployment
- The repository includes a `Dockerfile` (at repo root) to build a container image:
  ```bash
  docker build -t ticket-triage-agent:latest .
  docker run --rm -p 8000:8000 --env-file .env ticket-triage-agent:latest
  ```
- Deployment targets:
  - **GCP Cloud Run** for serverless containers with autoscaling.
  - **AWS ECS / Fargate** for container orchestration.
  - **Kubernetes (EKS/GKE/AKS)** for advanced, multi-region deployments.
- Scaling model:
  - Horizontally scale stateless FastAPI instances behind a load balancer.
  - Use an autoscaler based on CPU and request latency.
  - Offload vector search to a managed vector DB (Pinecone, Weaviate, etc.) for large KBs.

### 2) Logging & Monitoring
- Basic structured logging is enabled in `app/main.py` using Python `logging`.
- Production recommendations:
  - Ship logs to a centralized log system (Datadog, Cloud Logging, ELK).
  - Instrument metrics (request latency, model call counts, error rates) with Prometheus/OpenTelemetry.
  - Use a tracing solution (OpenTelemetry / LangSmith) to trace LLM calls and measure costs and latencies.
  - Configure alerting for error spikes, high latency, or unexpected cost increases (PagerDuty).

### 3) Configuration & Secrets
- Local dev: use `.env` copied from `.env.example` (do NOT commit `.env`).
- Production: store secrets in a secret manager:
  - AWS Secrets Manager / Parameter Store
  - GCP Secret Manager
  - Azure Key Vault
- Inject secrets as environment variables at runtime; do not bake secrets into images.
- Use typed configuration (Pydantic `BaseSettings`) for robust environment handling.

### 4) Latency, Cost & Rate Limiting
- Minimize LLM calls by using embedding-based KB search for the heavy-lifting.
- Cache embeddings and common model responses (short TTL) to reduce repeated calls.
- For bursts, use asynchronous workers and batch embedding requests when possible.
- Use a Redis-backed rate limiter for production (example: `fastapi-limiter` or custom middleware).
- Track per-model call cost metrics and set spending alerts.

### 5) Reliability & Resilience
- Add retries with exponential backoff for transient LLM/network errors.
- Add circuit-breaker behavior for external model endpoints to avoid cascading failures.
- Store important events in durable logs or persistent queue (e.g., SQS, Pub/Sub) if needed.

### 6) Security & Privacy
- Avoid storing PII in logs; mask sensitive fields.
- Use HTTPS everywhere and enforce TLS for external model and vector DB communication.
- Rotate API keys regularly and use least privilege IAM roles for cloud resources.

---

If you'd like, I can:
- write the `Dockerfile` into your repository (done),
- commit these changes to the local repo copy (I cannot run git here),
- or prepare a ZIP of the updated project with these files included.
