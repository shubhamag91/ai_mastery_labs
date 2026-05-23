## 🔀 Lab 2: The Stateful Multi-Agent Automation Worker

### [Lab-2.1] Expose Custom Local Tools via FastMCP Server
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 3h
*   **Description:**
    Create a custom Model Context Protocol (MCP) server that exposes local operations (file reads/writes, folder scans) to any LLM engine.

    #### Tasks:
    - [ ] Set up a Python virtual environment and install `mcp` (or `@modelcontextprotocol/sdk` in Node).
    - [ ] Implement `read_inbox_newsletter(label)` tool: reads mock email newsletter text files from a local directory.
    - [ ] Implement `write_briefing_to_disk(filename, content)` tool: writes the finalized reports as markdown files on disk.
    - [ ] Test the server locally using the **MCP Inspector** (`npx @modelcontextprotocol/inspector`) to call tools and verify inputs/outputs.
    - [ ] Configure `mcp.json` to link the server to Claude Code or Cursor.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is stdio transport in the context of MCP? How does it differ from HTTP/SSE transport?
    - **Destructive Testing:** Write a tool that throws an unhandled exception or enters an infinite loop. Call it from the inspector and observe how the system catches the failure.