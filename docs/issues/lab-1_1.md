## 📘 Lab 1: The Production-Grade Enterprise RAG & Extraction Engine

### [Lab-1.1] Boot Dockerized Postgres + pgvector Infrastructure
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Set up a local, containerized PostgreSQL database configured with the `pgvector` extension. This serves as the data foundation for the RAG and structured profile extraction application.

    #### Tasks:
    - [ ] Create `docker-compose.yml` with a `postgres` service using an image that supports `pgvector` (e.g., `ankane/pgvector`).
    - [ ] Configure database environment variables securely via `.env`.
    - [ ] Write a Python/TypeScript database migration script using an ORM to define a `Candidate` table.
    - [ ] The `Candidate` table must include standard fields (ID, Name, Email) and a vector field `vector_embedding` of dimension `1536` (matching OpenAI embeddings).
    - [ ] Run `docker-compose up` and confirm Postgres is active and `pgvector` extension is successfully loaded.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is the mathematical difference between Cosine Similarity and L2 (Euclidean) Distance? When is each preferred?
    - **Destructive Testing:** Limit database container memory to `128MB`, load 50k dummy vectors, and run 50 parallel vector queries. Read and analyze the container error logs.