## 🛠️ Lab 4: The Local "AI Executive Assistant" (MCP & Custom Tool Use)

### [Lab-4.1] Setup FastMCP Server and Build Weather Fetching Tool
*   **Tag:** `Lab`
*   **Priority:** High
*   **Estimate:** 2h
*   **Description:**
    Initialize your local MCP server environment and build your first custom tool to fetch live weather forecasts from a public API.

    #### Tasks:
    - [ ] Create a virtual environment and install `mcp` (FastMCP).
    - [ ] Write a Python tool function `get_local_weather(city)` annotated with `@mcp.tool()`.
    - [ ] Use `requests` or `httpx` to retrieve live data from `https://wttr.in/` (or a similar free weather service) and format the text.
    - [ ] Run the FastMCP server in development mode.

    #### 🎓 Learning Checkpoint:
    *   **Self-Check Question:** What is the purpose of the docstring in the `@mcp.tool()` function? How does Claude/GPT use it to understand what the tool does?