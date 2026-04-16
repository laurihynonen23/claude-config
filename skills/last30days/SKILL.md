---
name: last30days
description: Recent-trends research assistant. Investigates any topic using signals from the last 30 days across Reddit, Twitter/X, YouTube, TikTok, Instagram, Bluesky, Hacker News, Polymarket, and the web. Produces a grounded, cited research briefing. Use this skill whenever someone wants to know what people are discussing, recommending, or debating right now — including queries like "best AI video tools", "latest on image generation", "cursor vs windsurf", "Claude Code skills", "what's hot in [topic]", or any request for recent trends, comparisons, recommendations, news, or prompting techniques. Also trigger for "what's everyone saying about X", "recent discussions on Y", or "what's the vibe on Z".
argument-hint: [query] [--agent]
---

# Last 30 Days Research

Discover what people are actually saying, posting, and betting on right now. Searches multiple public sources, scores for freshness and signal, and delivers a grounded report with citations.

## Step 1: Run config check

```bash
python3 ~/.claude/skills/last30days/hooks/validate_config.py
```

Warn the user if `SCRAPECREATORS_API_KEY` is missing — this disables social media fetching. Don't block on optional keys.

## Step 2: Parse intent

```bash
python3 ~/.claude/skills/last30days/scripts/intent_parser.py "$ARGUMENTS"
```

This returns a JSON object with:
- `query_type`: COMPARISON | PROMPTING | RECOMMENDATIONS | NEWS | GENERAL
- `topic`: normalized topic string
- `target_tool`: specific tool/platform if mentioned (e.g. "cursor")
- `topic_a` / `topic_b`: for COMPARISON queries

## Step 3: Show intro (skip if --agent flag present)

In normal mode, before fetching, show the user a brief structured acknowledgement:

```
🔍 Researching: [topic]
   Type: [query_type]
   Target: [target_tool or "not specified"]
   Sources: Reddit, Hacker News, Bluesky, YouTube, TikTok, Instagram, Twitter, Polymarket, web
   Window: last 30 days
```

This confirms your understanding before making API calls.

## Step 4: Optional entity handle resolution

If the topic is a person, product, creator, company, or tool — do a quick WebSearch to check if there's an official X/Twitter account. If found and clearly official (not a parody), note the handle for source retrieval. Skip this for generic concepts.

## Step 5: Fetch sources

```bash
python3 ~/.claude/skills/last30days/scripts/fetch_sources.py \
  --query "[topic]" \
  --days 30 \
  --sources all
```

The script returns JSON with an `items` array. Each item has:
- `source`: reddit | twitter | youtube | tiktok | instagram | bluesky | hackernews | polymarket | web
- `title`, `url`, `author`, `timestamp`, `excerpt`, `engagement`

Sources with missing credentials are automatically skipped and logged to stderr.

**For COMPARISON queries**: run fetch_sources.py twice — once for `topic_a`, once for `topic_b` — then synthesize together.

### WebSearch — always run this, especially when API keys are missing

Use WebSearch aggressively. It's the primary fallback when API sources are skipped and provides grounding regardless. Run these searches in parallel or sequence for every query:

| Platform missed | WebSearch query to run |
|---|---|
| Reddit | `site:reddit.com "[topic]" after:2025-02-22` |
| Twitter/X | `site:twitter.com OR site:x.com "[topic]" 2025` |
| YouTube | `site:youtube.com "[topic]" 2025` |
| TikTok | `site:tiktok.com "[topic]"` |
| General | `"[topic]" recent discussion OR review OR announcement 2025` |
| News/launches | `"[topic]" launched OR released OR announced March 2025` |

When API keys are missing (script returns mostly empty results), run **all 6** of the above. When APIs are available and return good results, run **2-3** targeted searches for gaps. Adjust date filters to the actual current date minus 30 days.

The goal is to have enough signal from real sources — Reddit threads, YouTube reviews, tweets, HN discussions — that the report is grounded in what people actually said, not generic knowledge.

## Step 6: Synthesize and write the report

Read the retrieved items and produce the report below. Prioritize:
1. **Cross-source convergence** — if Reddit, Bluesky, and HN all discuss the same thing, that's a strong signal
2. **High engagement** — posts with many upvotes, comments, or shares carry more weight
3. **Recency** — items from the past week outweigh items from 25 days ago
4. **Specificity** — concrete recommendations beat vague hype

Do not fabricate. If evidence is thin or conflicting, say so. If a source returned nothing, note it.

## Report structure

Use this template exactly:

```
# [Topic] — Last 30 Days

*Researched: [date] | Sources: [list of sources actually used]*

## Executive Summary
[2-4 sentences: what the last 30 days suggest about this topic]

## Strongest Signals
- [Most important finding, with source]
- [Second finding]
- [Third finding]
...

## What People Are Saying
[Group by source or theme. Include quotes, paraphrases, and links.]

### Reddit
...

### Hacker News
...

### Bluesky / Twitter
...

### YouTube / TikTok / Instagram
...

### Polymarket
[If relevant markets found: include question, current odds, and what the market implies]

## Key Examples
[3-5 specific posts, threads, videos, or articles worth clicking. Format: title, source, link, why it matters]

## Practical Takeaways
[3-5 actionable points based on retrieved evidence]

## [Mode-specific section — see below]

## Citations
[Numbered list of all sources cited inline]
```

## Mode-specific sections

### RECOMMENDATIONS
Add a **Ranked Options** section:
- Rank the top tools/products
- For each: why recommended, recent sentiment, tradeoffs, who it's for

### NEWS
Add a **Timeline** section:
- Sort findings by date
- Distinguish official announcements from community speculation

### PROMPTING
Add a **Prompt Patterns** section:
- Recurring structures or constraints that work
- Pitfalls to avoid
- 2-3 copy-ready prompt examples

If `target_tool` is known, optimize prompts for that tool. If not, give cross-tool patterns and note the gap.

### COMPARISON
Replace **What People Are Saying** with:

**[Topic A]**: summary, strengths, weaknesses, momentum
**[Topic B]**: summary, strengths, weaknesses, momentum

Add a **Head-to-Head** table:

| Dimension | [A] | [B] |
|---|---|---|
| Community sentiment | ... | ... |
| Recent buzz | ... | ... |
| Key use cases | ... | ... |
| Criticisms | ... | ... |

End with a **Verdict** based on retrieved evidence (not opinion).

## Step 7: Save the report

```bash
python3 ~/.claude/skills/last30days/scripts/save_report.py \
  --title "[topic]" \
  --content "[report markdown]"
```

This saves to `~/Documents/Last30Days/YYYY-MM-DD-[topic].md`. Tell the user where it was saved.

## Evidence rules

- Never present unsupported claims as facts
- Prefer direct links and primary sources
- Note uncertainty where evidence is thin or conflicting
- If a source was skipped due to missing credentials, say so briefly in the citations section
- Do not invent engagement numbers, dates, or quotes

## Config reference

Credentials are loaded from `.claude/last30days.env` (project-local) or `~/.claude/last30days.env` (global). Environment variables override file values.

| Variable | Required | Purpose |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | Required | Reddit, TikTok, Instagram, Bluesky, Twitter via API |
| `BRAVE_API_KEY` | Recommended | Web search, Twitter/YouTube fallback |
| `BSKY_HANDLE` + `BSKY_APP_PASSWORD` | Optional | Authenticated Bluesky (otherwise uses public API) |
| `TRUTHSOCIAL_TOKEN` | Optional | Truth Social access |
| `APIFY_API_TOKEN` | Optional | Alternative scraping fallback |

Credentials are never written to reports or logs.

## Running tests

```bash
python3 ~/.claude/skills/last30days/tests/test_intent_parser.py
python3 ~/.claude/skills/last30days/tests/test_config.py
python3 ~/.claude/skills/last30days/tests/test_scorer.py
```
