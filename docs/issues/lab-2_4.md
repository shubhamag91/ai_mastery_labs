### [Lab-2.4] Wrap Multi-Agent Graph with Secured FastAPI
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 2h
*   **Description:**
    Deploy your Langgraph automation runner behind a secured FastAPI web server with JWT/API-key authentication.

    #### Tasks:
    - [ ] Create a `/run-briefing` endpoint that runs the Langgraph in the background.
    - [ ] Add JWT authentication middleware to secure all endpoints.
    - [ ] Set up secure system prompt storage in MongoDB so instructions are not hardcoded in the codebase.