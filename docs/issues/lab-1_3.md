### [Lab-1.3] Build Semantic Search & Hybrid RAG Retrieval Endpoint
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Implement a `/search` endpoint that generates vector embeddings of a natural language query, performs a vector search inside Postgres using `pgvector`, retrieves the top candidates, and returns a generated comparative summary.

    #### Tasks:
    - [ ] Write an embeddings helper function that queries OpenAI `text-embedding-3-small` or uses a local sentence-transformer.
    - [ ] Write a raw SQL or ORM vector similarity query to retrieve the top 3 closest candidate records.
    - [ ] Create a `RAG Retriever` Pydantic AI agent.
    - [ ] Pass the retrieved database context and the original query to the agent to draft a highly tailored response summarizing why these candidates fit the query.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why is an HNSW (Hierarchical Navigable Small World) index faster than an IVFFlat index for vector searches? What are the tradeoffs in build time vs. recall accuracy?