### [Lab-2.2] Build Stateful Collaborative Multi-Agent Graph (Langgraph)
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 4h
*   **Description:**
    Build a multi-agent cooperative graph in **Langgraph** where specialized agents collaborate to analyze competitive updates, enforce self-correction, and output high-quality files using your custom MCP tools.

    #### Tasks:
    - [ ] Define the shared graph `State` to track raw research data, drafts, and critique logs.
    - [ ] Build a **Research Agent** that reads raw newsletters using the custom MCP tool.
    - [ ] Build an **Analyst Agent** that processes research data, formatting it into a clean markdown report.
    - [ ] Build a **QA Critic Agent** that checks the report for formatting, correctness, and details.
    - [ ] Establish a cycle: if the QA Critic rejects the report, the graph routes back to the Analyst Agent with instructions. Otherwise, it triggers the MCP write tool.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** How does Langgraph manage state updates? Why is "state reduction" (e.g. appending messages to a list) critical in a collaborative loop?