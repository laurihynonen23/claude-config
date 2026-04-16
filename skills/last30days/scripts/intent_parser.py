#!/usr/bin/env python3
"""
Intent parser for last30days skill.
Parses a free-form query into structured intent.

Usage:
    python3 scripts/intent_parser.py "best AI video tools"
    python3 scripts/intent_parser.py "cursor vs windsurf"
    python3 scripts/intent_parser.py "Claude Code prompts for cursor"

Output: JSON to stdout
"""

import sys
import re
import json

# Tools and platforms we can recognize as TARGET_TOOL
KNOWN_TOOLS = {
    "cursor", "windsurf", "claude", "claude code", "copilot", "github copilot",
    "chatgpt", "gpt-4", "gpt4", "gemini", "perplexity", "midjourney", "sora",
    "runway", "pika", "kling", "hailuo", "udio", "suno", "stable diffusion",
    "comfyui", "automatic1111", "dalle", "dall-e", "ideogram", "flux",
    "notion", "obsidian", "linear", "figma", "vercel", "supabase",
    "replit", "lovable", "bolt", "v0", "devin", "aider",
}

PROMPTING_SIGNALS = [
    "prompts", "prompt", "prompting", "how to prompt", "best prompt",
    "prompt engineering", "system prompt", "instructions", "techniques",
]

RECOMMENDATION_SIGNALS = [
    "best", "top", "recommend", "recommended", "which", "what should",
    "favorite", "alternatives", "options", "tools for", "apps for",
]

NEWS_SIGNALS = [
    "latest", "recent", "news", "update", "new", "just released",
    "announced", "launched", "release", "what happened", "trending",
]

COMPARISON_SIGNALS = [
    " vs ", " versus ", " or ", " compared to ", " vs. ",
]


def normalize(text: str) -> str:
    return text.lower().strip()


def detect_query_type(q: str) -> str:
    q_lower = normalize(q)

    for sig in COMPARISON_SIGNALS:
        if sig in q_lower:
            return "COMPARISON"

    for sig in PROMPTING_SIGNALS:
        if sig in q_lower:
            return "PROMPTING"

    for sig in RECOMMENDATION_SIGNALS:
        if q_lower.startswith(sig) or f" {sig} " in q_lower:
            return "RECOMMENDATIONS"

    for sig in NEWS_SIGNALS:
        if q_lower.startswith(sig) or f" {sig} " in q_lower:
            return "NEWS"

    return "GENERAL"


def extract_comparison_sides(q: str):
    """Extract TOPIC_A and TOPIC_B from comparison queries."""
    q_lower = normalize(q)
    for sep in [" vs ", " versus ", " vs. "]:
        if sep in q_lower:
            parts = q_lower.split(sep, 1)
            # Clean up "best X vs best Y" style
            a = re.sub(r"^(best|top|which is better|compare)\s+", "", parts[0].strip())
            b = parts[1].strip()
            return a.strip(), b.strip()
    return None, None


def extract_target_tool(q: str) -> str | None:
    """Find a known tool name in the query."""
    q_lower = normalize(q)

    # Pattern: "[topic] for [tool]" or "prompts for [tool]"
    for_match = re.search(r"\bfor\s+([a-z0-9\s\-]+?)(?:\s*$|\s+and\s+)", q_lower)
    if for_match:
        candidate = for_match.group(1).strip()
        if candidate in KNOWN_TOOLS:
            return candidate
        # Partial match
        for tool in sorted(KNOWN_TOOLS, key=len, reverse=True):
            if tool in candidate:
                return tool

    # General mention of a known tool anywhere in query
    for tool in sorted(KNOWN_TOOLS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(tool)}\b", q_lower):
            return tool

    return None


def extract_topic(q: str, query_type: str, topic_a: str = None, topic_b: str = None) -> str:
    """Derive a clean topic string."""
    if query_type == "COMPARISON":
        if topic_a and topic_b:
            return f"{topic_a} vs {topic_b}"

    q_lower = normalize(q)

    # Remove leading signal words
    for sig in RECOMMENDATION_SIGNALS + NEWS_SIGNALS:
        q_lower = re.sub(rf"^{re.escape(sig)}\s+", "", q_lower)

    # Remove "for [tool]" suffix if we extracted a tool
    q_lower = re.sub(r"\s+for\s+\w[\w\s\-]*$", "", q_lower).strip()

    return q_lower.strip()


def parse(query: str) -> dict:
    query_type = detect_query_type(query)
    topic_a, topic_b = extract_comparison_sides(query) if query_type == "COMPARISON" else (None, None)
    target_tool = extract_target_tool(query)
    topic = extract_topic(query, query_type, topic_a, topic_b)

    return {
        "raw_query": query,
        "topic": topic,
        "query_type": query_type,
        "target_tool": target_tool,
        "topic_a": topic_a,
        "topic_b": topic_b,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: intent_parser.py <query>"}))
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = parse(query)
    print(json.dumps(result, indent=2))
