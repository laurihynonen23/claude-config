---
name: site-content-extractor project
description: CLI tool for extracting client website content to hand off to a coding agent for rebuilding
type: project
---

Built a production-ready website content extraction CLI at `/Users/laurihynonen/site-content-extractor`.

**Why:** User is building new websites for clients and needs to extract all content from the old site and give it to a coding agent that rebuilds the new site.

**How to apply:** When the user mentions extracting a site, crawling a URL, or giving content to a building agent, this is the tool to use.

## How to run

```bash
cd /Users/laurihynonen/site-content-extractor
npm run dev -- crawl --url https://example.com --out ./output
```

Or just: user gives a URL, run it directly in the session.

## Key output files (in `output/domain-name/timestamp/`)

- `AGENT_CONTEXT.md` — the start-here file for the building agent. Global nav, footer, contact, full page inventory, notes
- `global/navigation.md`, `global/footer.md`, `global/contact.md` — shared components
- `groups/[prefix].md` — for repeating page types (e.g. blog posts): full inventory table + content summaries for all pages
- `_templates/[name].md` — template structure + 3 examples for repeating page types
- `pages/[slug]/page.md` — each page's unique content (lean: nav/footer stripped)
- `pages/[slug]/page.json` — same as structured JSON
- `pages/[slug]/raw.html` — original rendered HTML
- `pages/[slug]/screenshot.png` — visual snapshot

## Key design decisions

- Pages are rendered with Playwright (JS rendering on by default)
- For 50+ blog posts: all individual files still exist, but `groups/blog.md` has all content in one file so the agent doesn't need to open 50 files
- Template detection: groups URL-prefix siblings with low structural variance into a template
- Lean per-page files: nav and footer stripped from page.md, stored once in global/
- Respects robots.txt and parses sitemap.xml by default

## Tech stack

TypeScript, Node.js, Playwright, Cheerio, Commander, p-limit, fs-extra, Vitest. 97 tests passing.
