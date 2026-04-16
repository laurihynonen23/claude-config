"""Tests for config validation and env loading."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.fetch_sources import load_env, _parse_env_file


def test_parse_env_file_basic():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SCRAPECREATORS_API_KEY=test_key_123\n")
        f.write("BRAVE_API_KEY=brave_456\n")
        name = f.name

    # Unset to allow loading
    os.environ.pop("SCRAPECREATORS_API_KEY", None)
    os.environ.pop("BRAVE_API_KEY", None)

    _parse_env_file(Path(name))
    assert os.environ.get("SCRAPECREATORS_API_KEY") == "test_key_123"
    assert os.environ.get("BRAVE_API_KEY") == "brave_456"

    # Cleanup
    os.unlink(name)
    os.environ.pop("SCRAPECREATORS_API_KEY", None)
    os.environ.pop("BRAVE_API_KEY", None)


def test_parse_env_file_ignores_comments():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# This is a comment\n")
        f.write("MY_TEST_KEY=value\n")
        name = f.name

    os.environ.pop("MY_TEST_KEY", None)
    _parse_env_file(Path(name))
    assert os.environ.get("MY_TEST_KEY") == "value"

    os.unlink(name)
    os.environ.pop("MY_TEST_KEY", None)


def test_parse_env_file_strips_quotes():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('QUOTED_KEY="my_secret_value"\n')
        name = f.name

    os.environ.pop("QUOTED_KEY", None)
    _parse_env_file(Path(name))
    assert os.environ.get("QUOTED_KEY") == "my_secret_value"

    os.unlink(name)
    os.environ.pop("QUOTED_KEY", None)


def test_env_does_not_override_existing():
    os.environ["EXISTING_KEY"] = "original"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("EXISTING_KEY=overwritten\n")
        name = f.name

    _parse_env_file(Path(name))
    assert os.environ.get("EXISTING_KEY") == "original"

    os.unlink(name)
    os.environ.pop("EXISTING_KEY", None)


def test_parse_env_missing_file():
    # Should not raise
    _parse_env_file(Path("/nonexistent/path/file.env"))


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
