### [Lab-5.3] Integrate Local ChromaDB to Store Profiles
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Create a local semantic index using ChromaDB (or a simple SQLite vector store) to save candidate profiles and their text representation embeddings.

    #### Tasks:
    - [ ] Install `chromadb` (or use a lightweight SQLite schema with vector similarity).
    - [ ] Write an embeddings generation function using OpenAI's embedding API.
    - [ ] Extract profiles, generate embeddings for their aggregated skills/work history, and insert them into your local ChromaDB collection.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is an embedding vector? How does a vector database find records that are "semantically similar" without performing exact keyword matching?