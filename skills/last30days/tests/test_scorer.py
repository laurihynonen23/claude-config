"""Tests for deduplication and scoring logic in fetch_sources.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.fetch_sources import deduplicate, item


def make_item(source="reddit", title="Test post", url="https://example.com/1"):
    return item(source=source, title=title, url=url)


def test_deduplicate_removes_duplicate_urls():
    items = [
        make_item(title="Post Alpha", url="https://reddit.com/r/test/1"),
        make_item(title="Post Alpha Dupe", url="https://reddit.com/r/test/1"),  # same URL
        make_item(title="Post Beta", url="https://reddit.com/r/test/2"),
    ]
    result = deduplicate(items)
    assert len(result) == 2


def test_deduplicate_removes_duplicate_titles():
    items = [
        make_item(title="Amazing AI tool", url="https://site1.com/a"),
        make_item(title="Amazing AI tool", url="https://site2.com/b"),  # same title
    ]
    result = deduplicate(items)
    assert len(result) == 1


def test_deduplicate_keeps_unique_items():
    items = [
        make_item(title="Post A", url="https://reddit.com/1"),
        make_item(title="Post B", url="https://reddit.com/2"),
        make_item(title="Post C", url="https://hn.com/3"),
    ]
    result = deduplicate(items)
    assert len(result) == 3


def test_deduplicate_empty_list():
    assert deduplicate([]) == []


def test_deduplicate_trailing_slash_normalized():
    items = [
        make_item(url="https://example.com/post/"),
        make_item(url="https://example.com/post"),  # same URL, no trailing slash
    ]
    result = deduplicate(items)
    assert len(result) == 1


def test_item_truncates_long_title():
    long_title = "x" * 500
    it = item(source="reddit", title=long_title, url="https://example.com")
    assert len(it["title"]) <= 300


def test_item_truncates_long_excerpt():
    long_excerpt = "y" * 1000
    it = item(source="reddit", title="Test", url="https://example.com", excerpt=long_excerpt)
    assert len(it["excerpt"]) <= 500


def test_item_has_required_fields():
    it = item(source="hackernews", title="Launch HN: Something cool", url="https://hn.com/1")
    for field in ("source", "title", "url", "author", "timestamp", "excerpt", "engagement"):
        assert field in it


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
