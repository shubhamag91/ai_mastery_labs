from mcp.server.fastmcp import FastMCP
import httpx
import os

# Initialize FastMCP Server
mcp = FastMCP("Local Executive Assistant")

# Define the target todo.txt file path
TODO_PATH = os.path.expanduser("~/Desktop/todo.txt")

@mcp.tool()
async def get_local_weather(city: str) -> str:
    """
    Fetch the live weather forecast for a specified city.
    
    Args:
        city (str): The name of the city (e.g., 'Paris', 'New York', 'Tokyo').
    
    Returns:
        str: A single-line summary of the current weather in that city.
    """
    # Using wttr.in with ?format=3 for a concise single-line weather summary
    url = f"https://wttr.in/{city}?format=3"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            # wttr.in returns 200 even for invalid cities, but let's check basic errors
            if response.status_code == 200:
                content = response.text.strip()
                # Check for wttr.in error page indicator
                if "Unknown location" in content or "Location not found" in content:
                    return f"Error: Could not find weather information for '{city}'. Please verify the city name."
                return content
            else:
                return f"Error: Unable to fetch weather data (HTTP status code {response.status_code})."
    except httpx.RequestError as e:
        return f"Error: Network request failed: {str(e)}"

@mcp.tool()
def append_to_todo_list(task: str, priority: str = "Medium") -> str:
    """
    Append a new task to your local todo.txt file on the Desktop.
    
    Args:
        task (str): The description of the task to be added.
        priority (str): The urgency level of the task. Must be 'High', 'Medium', or 'Low'. Defaults to 'Medium'.
        
    Returns:
        str: A confirmation message indicating the task was added successfully.
    """
    # Strict validation of priority values
    valid_priorities = {"High", "Medium", "Low"}
    if priority.capitalize() not in valid_priorities:
        return f"Error: Invalid priority '{priority}'. Allowed values are: 'High', 'Medium', 'Low'."
    
    # Capitalize the priority to enforce uniformity
    priority_formatted = priority.capitalize()
    
    try:
        # Ensure target directory exists (especially for edge case testing/reproducibility)
        os.makedirs(os.path.dirname(TODO_PATH), exist_ok=True)
        
        # Append the task with priority formatting
        with open(TODO_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{priority_formatted}] {task.strip()}\n")
            
        return f"Success: Added task '{task.strip()}' with {priority_formatted} priority to your todo list."
    except Exception as e:
        return f"Error: Failed to write to todo.txt: {str(e)}"

@mcp.tool()
def read_todo_list() -> str:
    """
    Read all tasks currently saved in your local todo.txt file on the Desktop.
    
    Returns:
        str: A formatted list of tasks, or a message indicating the todo list is empty.
    """
    if not os.path.exists(TODO_PATH):
        return "Your todo list is currently empty. Add a task using `append_to_todo_list` to get started!"
    
    try:
        with open(TODO_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        if not content:
            return "Your todo list is currently empty."
            
        # Format the output beautifully for the LLM
        lines = content.split("\n")
        formatted_list = "Here is your current Todo List:\n"
        for i, line in enumerate(lines, 1):
            formatted_list += f"{i}. {line}\n"
            
        return formatted_list.strip()
    except Exception as e:
        return f"Error: Failed to read todo.txt: {str(e)}"

if __name__ == "__main__":
    # Run the FastMCP server (default stdio transport)
    mcp.run()
