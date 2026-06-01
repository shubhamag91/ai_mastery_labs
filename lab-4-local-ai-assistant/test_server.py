import asyncio
import os
import shutil
from server import get_local_weather, append_to_todo_list, read_todo_list, TODO_PATH

async def test_weather():
    print("\n--- Testing get_local_weather ---")
    
    # Test valid city
    print("Fetching weather for Tokyo...")
    tokyo_result = await get_local_weather("Tokyo")
    print(f"Tokyo weather: {tokyo_result}")
    
    # Test another valid city
    print("Fetching weather for London...")
    london_result = await get_local_weather("London")
    print(f"London weather: {london_result}")
    
    # Test invalid location (wttr.in output handling)
    print("Fetching weather for non-existent city 'NotACity12345'...")
    invalid_result = await get_local_weather("NotACity12345")
    print(f"Result for NotACity12345: {invalid_result}")

def test_todo():
    print("\n--- Testing Todo Operations ---")
    
    # Back up existing todo.txt if it exists
    backup_path = TODO_PATH + ".bak"
    has_backup = False
    if os.path.exists(TODO_PATH):
        print(f"Backing up existing todo.txt to {backup_path}")
        shutil.copyfile(TODO_PATH, backup_path)
        os.remove(TODO_PATH)
        has_backup = True
        
    try:
        # 1. Read empty list
        print("Reading empty todo list...")
        empty_read = read_todo_list()
        print(f"Result: {empty_read}")
        assert "empty" in empty_read.lower()
        
        # 2. Append task (Default priority)
        print("Adding task 'Complete Lab 4 code' (default priority)...")
        add_result = append_to_todo_list("Complete Lab 4 code")
        print(f"Result: {add_result}")
        assert "Success" in add_result
        
        # 3. Append task with High priority
        print("Adding task 'Review implementation plan' with High priority...")
        add_high = append_to_todo_list("Review implementation plan", "High")
        print(f"Result: {add_high}")
        
        # 4. Append task with invalid priority
        print("Adding task with invalid priority 'Urgent'...")
        add_invalid = append_to_todo_list("Invalid task", "Urgent")
        print(f"Result: {add_invalid}")
        assert "Error" in add_invalid
        
        # 5. Read todo list
        print("Reading updated todo list...")
        list_content = read_todo_list()
        print(list_content)
        assert "[Medium] Complete Lab 4 code" in list_content
        assert "[High] Review implementation plan" in list_content
        
    finally:
        # Clean up test todo file and restore backup if needed
        if os.path.exists(TODO_PATH):
            os.remove(TODO_PATH)
            
        if has_backup:
            print(f"Restoring backed up todo.txt from {backup_path}")
            shutil.copyfile(backup_path, TODO_PATH)
            os.remove(backup_path)
        print("Cleanup complete.")

async def main():
    await test_weather()
    test_todo()

if __name__ == "__main__":
    asyncio.run(main())
