### [Lab-1.4] Instrument Application with OpenTelemetry Tracing
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Expose full system visibility by instrumenting FastAPI and Pydantic AI with OpenTelemetry, sending traces to a local monitoring console in Docker (like Arize Phoenix or Langfuse).

    #### Tasks:
    - [ ] Boot an OpenTelemetry-compatible tracing server (Langfuse/Arize Phoenix) inside `docker-compose.yml`.
    - [ ] Install OpenTelemetry instrumentation packages for FastAPI and HTTP clients.
    - [ ] Instrument the Pydantic AI agent to track every LLM call, latency, system prompt configuration, and token count.
    - [ ] Verify that query traces appear in the tracing dashboard, mapping out the database calls and LLM calls in a unified timeline.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Revoke or corrupt your LLM API keys. Trigger a `/upload` endpoint request and inspect the telemetry dashboard traces. Analyze how the API error stack trace is captured and presented in the tracing system.