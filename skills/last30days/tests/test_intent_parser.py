"""Tests for intent_parser.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.intent_parser import parse


def test_comparison_vs():
    result = parse("cursor vs windsurf")
    assert result["query_type"] == "COMPARISON"
    assert "cursor" in result["topic_a"]
    assert "windsurf" in result["topic_b"]


def test_comparison_versus():
    result = parse("Claude versus GPT-4")
    assert result["query_type"] == "COMPARISON"


def test_recommendations_best():
    result = parse("best AI video tools")
    assert result["query_type"] == "RECOMMENDATIONS"


def test_prompting():
    result = parse("Claude Code prompts for cursor")
    assert result["query_type"] == "PROMPTING"


def test_prompting_target_tool():
    result = parse("midjourney prompts for portrait photography")
    assert result["query_type"] == "PROMPTING"


def test_news():
    result = parse("latest on image generation")
    assert result["query_type"] == "NEWS"


def test_general():
    result = parse("Claude Code skills")
    assert result["query_type"] == "GENERAL"


def test_target_tool_for_pattern():
    result = parse("best prompts for cursor")
    assert result["target_tool"] == "cursor"


def test_target_tool_mentioned():
    result = parse("how to use midjourney effectively")
    assert result["target_tool"] == "midjourney"


def test_no_target_tool():
    result = parse("best AI video tools")
    assert result["target_tool"] is None


def test_topic_extracted():
    result = parse("best AI video tools")
    assert "ai video tools" in result["topic"]


def test_raw_query_preserved():
    q = "latest Claude Code updates"
    result = parse(q)
    assert result["raw_query"] == q


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
