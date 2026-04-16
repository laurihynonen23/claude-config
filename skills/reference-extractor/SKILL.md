---
name: reference-extractor
description: Extract a cleaned visual/design reference package from a public URL for use as a reference when building a new site. Trigger when the user gives a URL they want to use as a design or visual reference, says "use this as reference", "extract reference from [url]", "I want to reference [url]", or similar. This is NOT for extracting client site content — use site-content-extractor for that.
argument-hint: <url> [flags]
---

# Reference Extractor

Turn a public URL into a cleaned, agent-friendly design reference package — sanitized HTML/CSS, section screenshots, component artifacts, and a reference brief. Used when you want to study a site's layout and visual patterns without cloning it.

## Tool location

```
/Users/laurihynonen/Projects/reference-extractor
```

Runs from the pre-built dist (no tsx needed):

```bash
cd /Users/laurihynonen/Projects/reference-extractor
node dist/cli.js extract --url <URL> --out ./output
```

## Workflow

1. **Get the URL** — from `$ARGUMENTS` or ask the user.
2. **Run the extractor** (defaults: representative crawl, up to 25 pages, desktop + mobile):
   ```bash
   cd /Users/laurihynonen/Projects/reference-extractor && node dist/cli.js extract --url <URL> --out ./output
   ```
3. **Report the output path** — tell the user the timestamped folder and highlight the key files to hand off to the coding agent.

## Useful flags

| Flag | Purpose |
|---|---|
| `--max-pages <n>` | Limit pages crawled (default 25) |
| `--single-page` | Only extract the seed URL, no crawling |
| `--crawl-mode exhaustive` | Crawl more pages instead of diverse sampling |
| `--no-mobile` | Skip mobile screenshots |
| `--no-interactions` | Skip interaction capture (faster) |
| `--resume` | Resume the latest incomplete run for the same domain |
| `--concurrency <n>` | Parallel browser workers |
| `--include <pattern>` | Only crawl URLs matching pattern |
| `--exclude <pattern>` | Skip URLs matching pattern |

## Output structure

All files land in `output/<domain-slug>/<timestamp>/`:

| Path | Purpose |
|---|---|
| `manifest.json` | Full run metadata |
| `audit.md` | Fidelity and extraction notes |
| `run-state.json` | Resume state |
| `cleaned/<page-id>/reference.html` | Sanitized HTML |
| `cleaned/<page-id>/reference.css` | Pruned CSS |
| `cleaned/<page-id>/desktop.png` | Clean render screenshot |
| `raw/<page-id>/rendered.html` | Original rendered HTML |
| `sections/<page-id>/<section-slug>/` | Per-section HTML, CSS, JSON, screenshot |
| `components/<component-id>/` | Repeated shared components |
| `notes/reference-brief.json` | Compact downstream brief — start here |
| `notes/templates.json` | Template groupings |
| `notes/site-map.json` | Crawled URL map |

## What to hand off to a coding agent

- `notes/reference-brief.json` — compact overview, start here
- `components/` — shared patterns (header, footer, cards)
- `cleaned/<page-id>/reference.html` + `reference.css`
- `sections/<page-id>/...` — section-level detail
- `audit.md` — what was stripped and why

## Key difference from site-content-extractor

- **site-content-extractor** → extracts *text content* from a client's site to rebuild it (nav, page copy, blog posts)
- **reference-extractor** → extracts *visual/design reference* from any public site (layout, CSS, sections, components)
