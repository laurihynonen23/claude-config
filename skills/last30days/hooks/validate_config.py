#!/usr/bin/env python3
"""
Session-start config validation hook for last30days skill.
Checks for required/optional credentials and warns on issues.
Does NOT send credentials anywhere.

Usage:
    python3 hooks/validate_config.py
"""

import os
import stat
import sys
from pathlib import Path


REQUIRED = ["SCRAPECREATORS_API_KEY"]

OPTIONAL = {
    "BRAVE_API_KEY": "Web search + Twitter/YouTube fallback",
    "APIFY_API_TOKEN": "Alternative social media scraping",
    "BSKY_HANDLE": "Bluesky authenticated search",
    "BSKY_APP_PASSWORD": "Bluesky authenticated search",
    "TRUTHSOCIAL_TOKEN": "Truth Social access",
    "OPENAI_API_KEY": "OpenAI-based synthesis (optional)",
    "XAI_API_KEY": "xAI/Grok synthesis (optional)",
    "OPENROUTER_API_KEY": "OpenRouter model access (optional)",
}

ENV_FILES = [
    Path(".claude/last30days.env"),          # project-local (preferred)
    Path.home() / ".claude" / "last30days.env",  # global fallback
]


def load_env_file(path: Path):
    """Load key=value pairs from an env file into os.environ."""
    if not path.exists():
        return False
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
        return True
    except Exception:
        return False


def check_file_permissions(path: Path) -> list[str]:
    """Return warnings if the file is world- or group-readable."""
    warnings = []
    try:
        mode = path.stat().st_mode
        if mode & stat.S_IRGRP:
            warnings.append(f"  ⚠️  {path} is group-readable (chmod 600 recommended)")
        if mode & stat.S_IROTH:
            warnings.append(f"  ⚠️  {path} is world-readable (chmod 600 recommended)")
    except Exception:
        pass
    return warnings


def validate():
    issues = []
    warnings = []
    notes = []

    # Load env files (project-local first)
    loaded_file = None
    for env_file in ENV_FILES:
        if load_env_file(env_file):
            loaded_file = env_file
            perm_warns = check_file_permissions(env_file)
            warnings.extend(perm_warns)
            break

    if loaded_file:
        notes.append(f"  ✓ Loaded config from: {loaded_file}")
    else:
        notes.append("  ℹ️  No .claude/last30days.env found — using environment variables only")
        notes.append("     Create ~/.claude/last30days.env to set credentials persistently")

    # Check required keys
    for key in REQUIRED:
        if not os.environ.get(key):
            issues.append(f"  ✗ REQUIRED: {key} is not set — social media sources will be unavailable")

    # Check optional keys
    missing_optional = []
    for key, purpose in OPTIONAL.items():
        if not os.environ.get(key):
            missing_optional.append(f"  ○ {key}: {purpose}")

    # Print report
    print("\n━━━ last30days config check ━━━")
    for note in notes:
        print(note)

    if issues:
        print("\n[ERRORS — will degrade functionality]")
        for issue in issues:
            print(issue)

    if warnings:
        print("\n[WARNINGS — security]")
        for warn in warnings:
            print(warn)

    if missing_optional:
        print("\n[Optional keys not set — some sources will be skipped]")
        for m in missing_optional:
            print(m)

    if not issues and not warnings:
        print("  ✓ All required keys present")

    print()

    # Exit non-zero only if required keys are missing
    if issues:
        sys.exit(1)


if __name__ == "__main__":
    validate()
