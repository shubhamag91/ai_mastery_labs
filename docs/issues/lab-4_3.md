### [Lab-4.3] Test and Debug MCP Server via MCP Inspector
*   **Tag:** `Lab`
*   **Priority:** Medium
*   **Estimate:** 1h
*   **Description:**
    Use the official Model Context Protocol Inspector to visually test, debug, and validate your tools' input schemas and outputs in isolation.

    #### Tasks:
    - [ ] Start your FastMCP server in your terminal.
    - [ ] Boot the inspector dashboard using `npx @modelcontextprotocol/inspector`.
    - [ ] Call `get_local_weather` with test inputs and inspect the JSON schema validation.
    - [ ] Call `append_to_todo_list` and verify the output payload is correct and matches FastMCP specs.

    #### 🎓 Learning Checkpoint:
    - **Destructive Testing:** Send null or malformed data inside the inspector to your todo tool. Analyze the JSON-RPC error responses returned to the client and fix any unhandled exceptions.