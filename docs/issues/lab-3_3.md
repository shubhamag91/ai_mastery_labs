### [Lab-3.3] Deploy Model Locally inside Docker (Ollama)
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Serve your compiled custom model inside a containerized local environment using Ollama, exposing an OpenAI-compatible API interface.

    #### Tasks:
    - [ ] Add an `ollama` container service to `docker-compose.yml`.
    - [ ] Write a custom `Modelfile` detailing system prompts, parameters (temperature), and the path to your GGUF file.
    - [ ] Load and register your custom model inside the Ollama container.
    - [ ] Expose endpoint `11434` and verify model connectivity via curl requests.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Bombard your local Ollama server with 50 parallel inference queries using a shell loop. Track resource consumption with `docker stats` and note the latency impact.