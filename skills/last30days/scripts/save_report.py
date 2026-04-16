#!/usr/bin/env python3
"""
Save a research report to ~/Documents/Last30Days/

Usage:
    python3 scripts/save_report.py --title "AI video tools" --content "# AI video tools\n..."
    echo "report content" | python3 scripts/save_report.py --title "my topic"

Output: JSON with saved_path key, or error key.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def safe_filename(title: str) -> str:
    """Convert a topic title to a safe filename."""
    slug = re.sub(r"[^\w\s\-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:80]


def save_report(title: str, content: str, output_dir: str = None) -> dict:
    if not output_dir:
        output_dir = str(Path.home() / "Documents" / "Last30Days")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{safe_filename(title)}.md"
    filepath = out_path / filename

    # Handle filename collisions
    if filepath.exists():
        i = 2
        while filepath.exists():
            filepath = out_path / f"{date_str}-{safe_filename(title)}-{i}.md"
            i += 1

    filepath.write_text(content, encoding="utf-8")

    return {
        "saved_path": str(filepath),
        "filename": filepath.name,
        "directory": str(out_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Topic/title for filename")
    parser.add_argument("--content", help="Report markdown content (or pipe via stdin)")
    parser.add_argument("--dir", help="Output directory (default: ~/Documents/Last30Days)")
    args = parser.parse_args()

    content = args.content
    if not content:
        content = sys.stdin.read()

    if not content.strip():
        print(json.dumps({"error": "No content provided"}))
        sys.exit(1)

    result = save_report(args.title, content, args.dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
