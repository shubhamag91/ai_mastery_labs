import os
import re
import subprocess

# Paths
BACKLOG_PATH = "/Users/shubham/Projects/ai_mastery_labs/linear_backlog_labs.md"
DOCS_DIR = "/Users/shubham/Projects/ai_mastery_labs/docs/issues"
PROJECT_ID = "adcc5703d02c"  # Lab project ID
TEAM_KEY = "MOS"

os.makedirs(DOCS_DIR, exist_ok=True)

# Priority mapping (1: urgent, 2: high, 3: medium, 4: low)
PRIORITY_MAP = {
    "critical": "1",
    "urgent": "1",
    "high": "2",
    "medium": "3",
    "low": "4",
}

with open(BACKLOG_PATH, "r") as f:
    content = f.read()

# Split content by issue block separator "---"
sections = content.split("\n---\n")

issues = []

for idx, section in enumerate(sections):
    # Parse title (lines starting with ### [Lab-x.y] or similar)
    title_match = re.search(r"###\s+\[(Lab-\d\.\d)\]\s+(.+)", section)
    if not title_match:
        continue
    
    label_tag = title_match.group(1)  # e.g., "Lab-1.1"
    raw_title = title_match.group(2).strip()
    full_title = f"[{label_tag}] {raw_title}"
    
    # Parse metadata
    priority_match = re.search(r"\*\s+Priority:\s+(\w+)", section, re.IGNORECASE)
    estimate_match = re.search(r"\*\s+Estimate:\s+(\d+)", section)
    
    priority_str = priority_match.group(1).lower() if priority_match else "medium"
    priority_val = PRIORITY_MAP.get(priority_str, "3")
    
    estimate_val = estimate_match.group(1) if estimate_match else "1"
    
    # Parse description (content after the metadata block)
    # The description starts after the list bullet for Description:
    desc_start_match = re.search(r"\*\s+Description:\s*\n", section, re.IGNORECASE)
    if desc_start_match:
        description_text = section[desc_start_match.end():].strip()
    else:
        # Fallback
        description_text = section.strip()
        
    issue_filename = f"{label_tag.lower().replace('.', '_')}.md"
    desc_file_path = os.path.join(DOCS_DIR, issue_filename)
    
    with open(desc_file_path, "w") as df:
        df.write(description_text)
        
    issues.append({
        "title": full_title,
        "priority": priority_val,
        "estimate": estimate_val,
        "desc_file": desc_file_path,
        "tag": label_tag
    })

print(f"Parsed {len(issues)} issues. Starting Linear import...")

for issue in issues:
    cmd = [
        "linear", "issue", "create",
        "--title", issue["title"],
        "--project", PROJECT_ID,
        "--team", TEAM_KEY,
        "--label", "Lab",
        "--estimate", issue["estimate"],
        "--priority", issue["priority"],
        "--description-file", issue["desc_file"],
        "--no-interactive"
    ]
    
    print(f"Creating issue: {issue['title']} (Estimate: {issue['estimate']}, Priority: {issue['priority']})...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Successfully created: {issue['title']}\n{result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue {issue['title']}: {e.stderr}")

print("Linear issues import process complete!")
