### [Lab-4.2] Build Local Todo List Operations Tool
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Add a local file-writing tool to your custom FastMCP server, allowing the agent to read and append to a raw text file on your filesystem.

    #### Tasks:
    - [ ] Write a Python tool function `append_to_todo_list(task, priority)` annotated with `@mcp.tool()`.
    - [ ] Implement file lock/handling logic to safely write tasks into a local `todo.txt` on your Desktop.
    - [ ] Add a companion tool `read_todo_list()` to read and return the contents of `todo.txt` in a formatted structure.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What security risks are associated with letting an LLM write or edit files directly on your local system? How does the MCP client permission dialog mitigate this?