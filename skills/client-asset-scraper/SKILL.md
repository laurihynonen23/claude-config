---
name: client-asset-scraper
description: Scrape and download logo and key images from a client's existing website. Trigger when given an existing site URL and need to extract brand assets (logo, hero, key visuals) for a redesign. Also triggered as Phase 1d inside new-site-from-brief.
argument-hint: "<site-url> [company-slug] [output-dir]"
---

# Client Asset Scraper

Extract the client's logo and key images from their existing website and download them locally.

## What it extracts

| Priority | Target | How to find |
|---|---|---|
| 1 | Logo (SVG) | Inline `<svg>` in `<header>` or `<nav>` |
| 2 | Logo (img) | `<img>` inside `<header>` or `<nav>` — especially with "logo" in class/id/alt/src |
| 3 | Social image | `<meta property="og:image">` content |
| 4 | Favicon (hires) | `<link rel="apple-touch-icon">` or `<link rel="icon" type="image/png">` |
| 5 | Hero image | First large `<img>` or `background-image` in a hero/banner section |
| 6 | Key visuals | Featured images in services/portfolio sections |

Stop at 10 images total. Skip icons < 32px, tracking pixels, spacer gifs.

## Output directory

Default: `~/client-assets/<company-slug>/`

Use `--out` override if provided.

## Step-by-step

### 1 — Fetch the page

Use WebFetch on the site URL. Read the full HTML response.

### 2 — Extract asset URLs

From the HTML, identify candidates in priority order above. For each candidate:
- Resolve relative URLs to absolute (prepend `https://domain.com` if path starts with `/`)
- Note what type it is (logo, og-image, hero, etc.)
- Note the element context (header img, meta tag, etc.)

Build a list: `[{ url, type, context }]`

### 3 — Download assets

```bash
mkdir -p ~/client-assets/<slug>/
```

For each asset URL:
```bash
curl -L -s -o ~/client-assets/<slug>/<filename> "<url>"
```

Derive `<filename>` from the URL path. If URL has no useful filename, use `<type>-<n>.<ext>`.

For SVG logos found inline (not a URL), save the raw SVG markup:
```bash
cat > ~/client-assets/<slug>/logo.svg << 'EOF'
<svg ...>...</svg>
EOF
```

### 4 — Report manifest

After downloading, print a summary:

```
Client assets saved to: ~/client-assets/<slug>/

  logo.svg          ← inline SVG from <header>
  og-image.jpg      ← og:image meta
  hero.jpg          ← first hero section img
  apple-touch-icon.png ← apple-touch-icon link

4 assets downloaded.
```

If nothing useful found, say so and suggest running stock-fetcher instead.

## Notes

- Client's own site = their assets. No copyright concern.
- If the page uses a JS-rendered logo (blank `<img>` src, loads via JS), WebFetch won't see it — note this in the report.
- Prefer SVG over PNG/JPG for logos — scales better for redesign use.
- og:image is often the best single hero/branding image even if it's not the actual logo.
