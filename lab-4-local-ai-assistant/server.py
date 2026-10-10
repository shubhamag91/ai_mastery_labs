from fastmcp import FastMCP

import os

# Initialize the MCP Server
# The nameplate "Weather_And_Tasks" tells the AI exactly what tools are inside.
mcp = FastMCP("Weather_And_Tasks")

# Define where our tasks will be saved
TODO_FILE = "todo.txt"

@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a specific location."""
    # We are hardcoding this for the lab, but in a real app, you would call a Weather API here!
    return f"The weather in {location} is currently 72 degrees and sunny."

@mcp.tool()
def add_todo(task: str) -> str:
    """Add a new task to the user's local to-do list file."""
    with open(TODO_FILE, "a") as f:
        f.write(f"- {task}\n")
    return f"Success! Added '{task}' to your to-do list."

@mcp.tool()
def list_todos() -> str:
    """Read the user's local to-do list file and return all current tasks."""
    if not os.path.exists(TODO_FILE):
        return "Your to-do list is currently empty!"
    
    with open(TODO_FILE, "r") as f:
        tasks = f.read()
    return tasks

if __name__ == "__main__":
    # This runs the server using standard input/output, which is how MCP communicates locally
    print("Starting MCP Server...", flush=True)
    mcp.run()
