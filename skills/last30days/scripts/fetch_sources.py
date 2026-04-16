#!/usr/bin/env python3
"""
Multi-source fetcher for last30days skill.
Retrieves recent content from Reddit, Twitter/X, YouTube, TikTok,
Instagram, Bluesky, Hacker News, Polymarket, and web.

Usage:
    python3 scripts/fetch_sources.py --query "AI video tools" [--days 30] [--sources all]

--sources: comma-separated list of: reddit,twitter,youtube,tiktok,instagram,
           bluesky,hackernews,polymarket,web
           Use "all" for all available sources (default).

Output: JSON to stdout — list of result items.
Credentials are read from environment variables (or .claude/last30days.env if present).

Exit codes:
  0 - success (even if some sources skipped)
  1 - fatal error (no query, missing required key)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error


# ─── Credential loader ────────────────────────────────────────────────────────

def load_env(project_root: Path = None):
    """Load credentials: check .claude/last30days.env first, then environment."""
    search_paths = []
    if project_root:
        search_paths.append(project_root / ".claude" / "last30days.env")
    search_paths.append(Path.home() / ".claude" / "last30days.env")

    for path in search_paths:
        if path.exists():
            _parse_env_file(path)
            break  # first match wins


def _parse_env_file(path: Path):
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)  # don't override real env vars
    except Exception:
        pass


def get_key(name: str) -> str | None:
    return os.environ.get(name) or None


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def http_get(url: str, headers: dict = None, timeout: int = 15) -> dict | list | None:
    """Simple GET request, returns parsed JSON or None on error."""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 402:
            print(f"[warn] Credit exhausted for {url}", file=sys.stderr)
        elif e.code == 401:
            print(f"[warn] Auth failed for {url}", file=sys.stderr)
        else:
            print(f"[warn] HTTP {e.code} for {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[warn] Request failed for {url}: {e}", file=sys.stderr)
        return None


SCRAPE_BASE = "https://api.scrapecreators.com"

def scrape(path: str, params: dict = None) -> dict | list | None:
    """Call ScrapeCreators API."""
    api_key = get_key("SCRAPECREATORS_API_KEY")
    if not api_key:
        return None

    qs = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
    url = f"{SCRAPE_BASE}{path}"
    if qs:
        url = f"{url}?{qs}"

    return http_get(url, headers={"x-api-key": api_key})


# ─── Timestamp helpers ────────────────────────────────────────────────────────

def cutoff_ts(days: int) -> int:
    """Unix timestamp for <days> ago."""
    return int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())


def ts_to_iso(ts) -> str:
    if ts is None:
        return ""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
    except Exception:
        return str(ts)


def item(
    source: str,
    title: str,
    url: str,
    author: str = "",
    timestamp: str = "",
    excerpt: str = "",
    engagement: dict = None,
) -> dict:
    return {
        "source": source,
        "title": title[:300] if title else "",
        "url": url,
        "author": author,
        "timestamp": timestamp,
        "excerpt": excerpt[:500] if excerpt else "",
        "engagement": engagement or {},
    }


# ─── Source fetchers ──────────────────────────────────────────────────────────

def fetch_reddit(query: str, days: int) -> list:
    results = []
    data = scrape("/v1/reddit/search", {"q": query, "timeframe": "month", "sort": "relevance"})
    if not data:
        return results

    posts = data if isinstance(data, list) else data.get("posts", data.get("data", []))
    ct = cutoff_ts(days)

    for p in posts[:20]:
        created = p.get("created_utc") or p.get("created") or 0
        if int(created or 0) < ct:
            continue
        results.append(item(
            source="reddit",
            title=p.get("title", ""),
            url=p.get("url") or p.get("permalink", ""),
            author=p.get("author", ""),
            timestamp=ts_to_iso(created),
            excerpt=p.get("selftext", "")[:300],
            engagement={
                "score": p.get("score", 0),
                "comments": p.get("num_comments", 0),
                "upvote_ratio": p.get("upvote_ratio", 0),
            },
        ))
    return results


def fetch_twitter(query: str, days: int) -> list:
    """
    ScrapeCreators Twitter exposes per-user tweets but not a general search.
    Use Brave Search API to surface recent Twitter threads if available.
    """
    results = []
    brave_key = get_key("BRAVE_API_KEY")
    if not brave_key:
        return results

    url = "https://api.search.brave.com/res/v1/web/search"
    params = urllib.parse.urlencode({
        "q": f"site:twitter.com OR site:x.com {query}",
        "count": 10,
        "freshness": "pd",  # past day — will broaden if few results
    })
    data = http_get(f"{url}?{params}", headers={
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_key,
    })
    if not data:
        return results

    for r in (data.get("web", {}).get("results") or [])[:10]:
        results.append(item(
            source="twitter",
            title=r.get("title", ""),
            url=r.get("url", ""),
            author=r.get("profile", {}).get("name", "") if isinstance(r.get("profile"), dict) else "",
            excerpt=r.get("description", ""),
        ))
    return results


def fetch_youtube(query: str, days: int) -> list:
    """Search YouTube via ScrapeCreators if endpoint available, else skip."""
    results = []
    # ScrapeCreators doesn't expose a general YouTube search in documented endpoints;
    # fall back to web search via Brave
    brave_key = get_key("BRAVE_API_KEY")
    if not brave_key:
        return results

    url = "https://api.search.brave.com/res/v1/web/search"
    params = urllib.parse.urlencode({
        "q": f"site:youtube.com {query}",
        "count": 8,
        "freshness": "pw",  # past week
    })
    data = http_get(f"{url}?{params}", headers={
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": brave_key,
    })
    if not data:
        return results

    for r in (data.get("web", {}).get("results") or [])[:8]:
        results.append(item(
            source="youtube",
            title=r.get("title", ""),
            url=r.get("url", ""),
            excerpt=r.get("description", ""),
        ))
    return results


def fetch_tiktok(query: str, days: int) -> list:
    results = []
    # TikTok keyword search via ScrapeCreators
    data = scrape("/v1/tiktok/search/videos", {"query": query, "cursor": 0})
    if not data:
        return results

    videos = data if isinstance(data, list) else data.get("videos", data.get("data", []))
    ct = cutoff_ts(days)

    for v in videos[:15]:
        created = v.get("createTime") or v.get("create_time") or 0
        if int(created or 0) < ct:
            continue
        author = v.get("author", {})
        author_name = author.get("uniqueId") or author.get("nickname", "") if isinstance(author, dict) else str(author)
        results.append(item(
            source="tiktok",
            title=v.get("desc", ""),
            url=f"https://www.tiktok.com/@{author_name}/video/{v.get('id', '')}",
            author=author_name,
            timestamp=ts_to_iso(created),
            engagement={
                "likes": v.get("stats", {}).get("diggCount", 0) if isinstance(v.get("stats"), dict) else 0,
                "comments": v.get("stats", {}).get("commentCount", 0) if isinstance(v.get("stats"), dict) else 0,
                "shares": v.get("stats", {}).get("shareCount", 0) if isinstance(v.get("stats"), dict) else 0,
                "views": v.get("stats", {}).get("playCount", 0) if isinstance(v.get("stats"), dict) else 0,
            },
        ))
    return results


def fetch_instagram(query: str, days: int) -> list:
    results = []
    data = scrape("/v2/instagram/reels/search", {"query": query})
    if not data:
        return results

    reels = data if isinstance(data, list) else data.get("reels", data.get("data", []))
    ct = cutoff_ts(days)

    for r in reels[:15]:
        taken_at = r.get("taken_at") or r.get("timestamp") or 0
        if int(taken_at or 0) < ct:
            continue
        user = r.get("user", {})
        username = user.get("username", "") if isinstance(user, dict) else ""
        code = r.get("code") or r.get("shortcode", "")
        results.append(item(
            source="instagram",
            title=r.get("caption", {}).get("text", "") if isinstance(r.get("caption"), dict) else r.get("caption", ""),
            url=f"https://www.instagram.com/reel/{code}/",
            author=username,
            timestamp=ts_to_iso(taken_at),
            engagement={
                "likes": r.get("like_count", 0),
                "comments": r.get("comment_count", 0),
                "plays": r.get("play_count", 0),
            },
        ))
    return results


def fetch_bluesky(query: str, days: int) -> list:
    """
    Bluesky public search API (no auth needed for basic search).
    """
    results = []
    try:
        params = urllib.parse.urlencode({"q": query, "limit": 25, "sort": "latest"})
        data = http_get(f"https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?{params}")
        if not data:
            return results

        posts = data.get("posts", [])
        ct = cutoff_ts(days)

        for p in posts:
            record = p.get("record", {})
            indexed_at = p.get("indexedAt", "")
            try:
                dt = datetime.fromisoformat(indexed_at.replace("Z", "+00:00"))
                if dt.timestamp() < ct:
                    continue
            except Exception:
                pass

            author = p.get("author", {})
            uri = p.get("uri", "")
            # Convert at-uri to bsky.app link
            handle = author.get("handle", "")
            rkey = uri.split("/")[-1] if "/" in uri else ""
            url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else ""

            results.append(item(
                source="bluesky",
                title=record.get("text", "")[:200],
                url=url,
                author=handle,
                timestamp=indexed_at,
                excerpt=record.get("text", ""),
                engagement={
                    "likes": p.get("likeCount", 0),
                    "reposts": p.get("repostCount", 0),
                    "replies": p.get("replyCount", 0),
                },
            ))
    except Exception as e:
        print(f"[warn] Bluesky fetch failed: {e}", file=sys.stderr)
    return results


def fetch_hackernews(query: str, days: int) -> list:
    """HN Algolia search API — no auth needed."""
    results = []
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        params = urllib.parse.urlencode({
            "query": query,
            "tags": "story",
            "numericFilters": f"created_at_i>{int(cutoff.timestamp())}",
            "hitsPerPage": 20,
        })
        data = http_get(f"https://hn.algolia.com/api/v1/search?{params}")
        if not data:
            return results

        for hit in data.get("hits", []):
            results.append(item(
                source="hackernews",
                title=hit.get("title", ""),
                url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                author=hit.get("author", ""),
                timestamp=hit.get("created_at", ""),
                engagement={
                    "points": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                },
            ))
    except Exception as e:
        print(f"[warn] HN fetch failed: {e}", file=sys.stderr)
    return results


def fetch_polymarket(query: str, days: int) -> list:
    """Polymarket public API — no auth needed."""
    results = []
    try:
        params = urllib.parse.urlencode({
            "q": query,
            "limit": 10,
            "active": "true",
        })
        data = http_get(f"https://gamma-api.polymarket.com/markets?{params}")
        if not data:
            return results

        markets = data if isinstance(data, list) else data.get("markets", [])
        for m in markets[:10]:
            results.append(item(
                source="polymarket",
                title=m.get("question", m.get("title", "")),
                url=f"https://polymarket.com/event/{m.get('slug', m.get('id', ''))}",
                excerpt=m.get("description", ""),
                engagement={
                    "volume": m.get("volume", 0),
                    "liquidity": m.get("liquidity", 0),
                    "outcomes": m.get("outcomes", []),
                    "outcomePrices": m.get("outcomePrices", []),
                },
            ))
    except Exception as e:
        print(f"[warn] Polymarket fetch failed: {e}", file=sys.stderr)
    return results


def fetch_web(query: str, days: int) -> list:
    """General web search via Brave Search API."""
    results = []
    brave_key = get_key("BRAVE_API_KEY")
    if not brave_key:
        return results

    try:
        params = urllib.parse.urlencode({
            "q": query,
            "count": 10,
            "freshness": "pm",  # past month
        })
        data = http_get(
            f"https://api.search.brave.com/res/v1/web/search?{params}",
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": brave_key,
            }
        )
        if not data:
            return results

        for r in (data.get("web", {}).get("results") or [])[:10]:
            results.append(item(
                source="web",
                title=r.get("title", ""),
                url=r.get("url", ""),
                excerpt=r.get("description", ""),
                timestamp=r.get("page_age", ""),
            ))
    except Exception as e:
        print(f"[warn] Web search failed: {e}", file=sys.stderr)
    return results


# ─── Deduplication ────────────────────────────────────────────────────────────

def deduplicate(items: list) -> list:
    """Remove near-duplicates by URL and title similarity."""
    seen_urls = set()
    seen_titles = set()
    out = []
    for it in items:
        url = it.get("url", "").rstrip("/").lower()
        title = "".join(it.get("title", "").lower().split())[:80]
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        out.append(it)
    return out


# ─── Main ─────────────────────────────────────────────────────────────────────

SOURCE_MAP = {
    "reddit": fetch_reddit,
    "twitter": fetch_twitter,
    "youtube": fetch_youtube,
    "tiktok": fetch_tiktok,
    "instagram": fetch_instagram,
    "bluesky": fetch_bluesky,
    "hackernews": fetch_hackernews,
    "polymarket": fetch_polymarket,
    "web": fetch_web,
}

ALL_SOURCES = list(SOURCE_MAP.keys())


def main():
    parser = argparse.ArgumentParser(description="Fetch recent content from multiple sources.")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days")
    parser.add_argument("--sources", default="all", help="Comma-separated sources or 'all'")
    args = parser.parse_args()

    # Load credentials
    load_env()

    # Resolve sources
    if args.sources.strip().lower() == "all":
        sources = ALL_SOURCES
    else:
        sources = [s.strip().lower() for s in args.sources.split(",")]
        unknown = [s for s in sources if s not in SOURCE_MAP]
        if unknown:
            print(json.dumps({"error": f"Unknown sources: {unknown}"}))
            sys.exit(1)

    # Check required credential
    if not get_key("SCRAPECREATORS_API_KEY"):
        print("[warn] SCRAPECREATORS_API_KEY not set — social media sources will be skipped", file=sys.stderr)

    # Fetch from each source
    all_items = []
    skipped = []
    for source in sources:
        try:
            fetched = SOURCE_MAP[source](args.query, args.days)
            if fetched is None:
                skipped.append(source)
            else:
                all_items.extend(fetched)
        except Exception as e:
            print(f"[warn] {source} fetch error: {e}", file=sys.stderr)
            skipped.append(source)

    all_items = deduplicate(all_items)

    result = {
        "query": args.query,
        "days": args.days,
        "sources_requested": sources,
        "sources_skipped": skipped,
        "total_items": len(all_items),
        "items": all_items,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
