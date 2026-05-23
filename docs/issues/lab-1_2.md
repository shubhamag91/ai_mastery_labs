### [Lab-1.2] Build FastAPI Profile Extractor with Pydantic AI & Caching
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Develop a FastAPI endpoint (`POST /upload`) that takes an unstructured resume, runs a schema-strict extraction using **Pydantic AI**, and saves the structured profile directly to PostgreSQL. Implement Prompt Caching to optimize costs and latency.

    #### Tasks:
    - [ ] Initialize a FastAPI application with structured routing.
    - [ ] Define nested Pydantic models: `DeveloperProfile`, `Skill` (name, category, years), `Experience` (company, role, duration), and `Education`.
    - [ ] Build a **Pydantic AI** extractor agent configured with a strict system prompt containing formatting guidelines and JSON outputs.
    - [ ] Implement ephemeral **Prompt Caching** on the Anthropic/OpenAI SDK calls so the system prompt and schema definitions are cached.
    - [ ] Write the FastAPI controller that triggers the agent, parses the resulting validated model, and inserts the relational data into Postgres.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Explain how prompt caching reduces costs on subsequent API requests. What specific headers or payload structures in the API response verify a cache hit?
    - **Destructive Testing:** Injects a dynamic timestamp variable into your system prompt on every call. Run 10 parallel runs, check API logs, and analyze the token cost spike.