---
name: site-content-extractor
description: Crawl a client website and extract structured content for a coding agent to rebuild it. Use whenever the user says "extract [site]", "crawl [url]", "use the site content extractor", or wants to grab content from a client's old site.
argument-hint: <url>
---

# Site Content Extractor

Crawl a public website and produce a structured content package ready for a coding agent to rebuild the site.

## Tool location

```
/Users/laurihynonen/site-content-extractor
```

Run with `tsx` (no build step needed):

```bash
cd /Users/laurihynonen/site-content-extractor
npm run dev -- crawl --url <URL> --out ./output
```

If `$ARGUMENTS` contains a URL, use it directly. Otherwise ask the user for the target URL before running.

## Workflow

1. **Get the URL** — from `$ARGUMENTS` or ask the user.
2. **Run the crawler:**
   ```bash
   cd /Users/laurihynonen/site-content-extractor && npm run dev -- crawl --url <URL> --out ./output
   ```
3. **Report the output location** — show the user the path to `AGENT_CONTEXT.md` inside the timestamped output folder. That's the file to hand off to the coding agent.

## Output structure

All files land in `output/<domain>/<timestamp>/`:

| File/folder | Purpose |
|---|---|
| `AGENT_CONTEXT.md` | **Start here.** Global nav, footer, contact, full page inventory, notes |
| `global/navigation.md` | Shared nav component |
| `global/footer.md` | Shared footer |
| `global/contact.md` | Contact info |
| `pages/<slug>/page.md` | Per-page content (nav/footer stripped) |
| `pages/<slug>/page.json` | Same content as structured JSON |
| `pages/<slug>/raw.html` | Original rendered HTML |
| `pages/<slug>/screenshot.png` | Visual snapshot |
| `groups/<prefix>.md` | For repeating page types (e.g. blog): full inventory + all content in one file |
| `_templates/<name>.md` | Template structure + 3 examples for repeating page types |

## Notes

- Pages are rendered with Playwright (JS rendering on).
- Sitemap and robots.txt are respected by default.
- For 50+ blog posts the individual files still exist, but `groups/blog.md` has everything in one file so the agent doesn't need to open 50 files.
- The lean `page.md` files have nav/footer stripped — stored once in `global/`.
