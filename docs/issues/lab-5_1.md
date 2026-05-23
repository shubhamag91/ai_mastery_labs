## 📂 Lab 5: The "Resume Scout" Pipeline (Structured Output & Caching)

### [Lab-5.1] Define Pydantic Schema and Build JSON Extractor Agent
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Define a strict data schema using Pydantic and write a script to extract unstructured resume text into a structured JSON object.

    #### Tasks:
    - [ ] Install the `openai` or `anthropic` Python SDK.
    - [ ] Define a Pydantic class `DeveloperProfile` containing lists of skills (name, years), experiences, and education.
    - [ ] Write a script that reads raw resume text and uses tool-calling/structured-outputs to return a validated `DeveloperProfile` instance.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** Why is Pydantic validation crucial when processing LLM-generated JSON outputs? What happens in your code if the LLM skips a required field?