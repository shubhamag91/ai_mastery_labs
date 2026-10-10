"""Push the issues in linear_backlog_labs.md to the Lab project in Linear.

Usage:
    python import_issues.py --dry-run              # show what would be created
    python import_issues.py --labs Lab-0 Lab-1     # create only these labs
    python import_issues.py                        # create everything not already in Linear

Safe to re-run: an issue is skipped when an issue with the same title already
exists in the project (canceled and duplicate issues don't count).
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKLOG_PATH = ROOT / "linear_backlog_labs.md"
DOCS_DIR = ROOT / "docs" / "issues"  # generated description files (gitignored)
PROJECT_ID = "adcc5703d02c"  # Lab project slug
TEAM_KEY = "MOS"

# Priority mapping (1: urgent, 2: high, 3: medium, 4: low)
PRIORITY_MAP = {
    "critical": "1",
    "urgent": "1",
    "high": "2",
    "medium": "3",
    "low": "4",
}

# Matches "### [Lab-2.1] Title", "### [Lab-10.P] Title" and "### [Milestone-1] Title"
TITLE_RE = re.compile(r"###\s+\[((?:Lab-\d+\.(?:\d+|P))|(?:Milestone-\d+))\]\s+(.+)")


def parse_backlog():
    """Return one dict per issue block in the backlog."""
    content = BACKLOG_PATH.read_text()
    issues = []

    for section in content.split("\n---\n"):
        title_match = TITLE_RE.search(section)
        if not title_match:
            continue

        tag = title_match.group(1)  # e.g. "Lab-2.P" or "Milestone-1"
        priority_match = re.search(r"\*\*Priority:\*\*\s*(\w+)", section, re.IGNORECASE)
        estimate_match = re.search(r"\*\*Estimate:\*\*\s*(\d+)", section)
        desc_start_match = re.search(r"\*\*Description:\*\*\s*\n", section, re.IGNORECASE)

        priority_str = priority_match.group(1).lower() if priority_match else "medium"
        description = (
            section[desc_start_match.end() :].strip() if desc_start_match else section.strip()
        )

        # The team doesn't use Linear's estimate field, so the estimate goes in the description.
        if estimate_match:
            description = f"**Estimate:** {estimate_match.group(1)}h\n\n{description}"

        issues.append(
            {
                "tag": tag,
                "group": tag.split(".")[0],  # "Lab-2" or "Milestone-1"
                "title": f"[{tag}] {title_match.group(2).strip()}",
                "priority": PRIORITY_MAP.get(priority_str, "3"),
                "description": description,
            }
        )

    return issues


def existing_titles():
    """Titles of live (not canceled or duplicate) issues already in the project."""
    # Keep the page sizes small: Linear rejects queries whose worst-case size is too large.
    query = (
        f'{{ projects(first: 1, filter: {{slugId: {{eq: "{PROJECT_ID}"}}}}) {{ nodes {{ '
        "issues(first: 200) { nodes { title state { type } } } } } }"
    )
    result = subprocess.run(["linear", "api", query], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)

    titles = set()
    for project in data["data"]["projects"]["nodes"]:
        for issue in project["issues"]["nodes"]:
            if issue["state"]["type"] not in ("canceled", "duplicate"):
                titles.add(issue["title"])
    return titles


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print what would be created; change nothing"
    )
    parser.add_argument(
        "--labs", nargs="+", metavar="GROUP", help="only these groups, e.g. Lab-0 Milestone-1"
    )
    args = parser.parse_args()

    issues = parse_backlog()
    if args.labs:
        issues = [i for i in issues if i["group"] in args.labs]

    already_there = existing_titles()
    to_create = [i for i in issues if i["title"] not in already_there]
    skipped = len(issues) - len(to_create)

    print(f"Parsed {len(issues)} issues; {skipped} already in Linear; {len(to_create)} to create.")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    for issue in to_create:
        desc_file = DOCS_DIR / f"{issue['tag'].lower().replace('.', '_')}.md"
        desc_file.write_text(issue["description"])

        if args.dry_run:
            print(f"  would create: {issue['title']} (priority {issue['priority']})")
            continue

        cmd = [
            "linear",
            "issue",
            "create",
            "--title",
            issue["title"],
            "--project",
            PROJECT_ID,
            "--team",
            TEAM_KEY,
            "--label",
            "Lab",
            "--priority",
            issue["priority"],
            "--description-file",
            str(desc_file),
            "--no-interactive",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Created: {issue['title']}\n{result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating {issue['title']}: {e.stderr}")

    if args.dry_run:
        print("Dry run: nothing was created.")


if __name__ == "__main__":
    main()
