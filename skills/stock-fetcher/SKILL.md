---
name: stock-fetcher
description: Fetch and download stock images from Unsplash by company name and themes. Trigger when the user says "find images for [company]", "fetch stock photos for [company]", "get pics for [company] with themes X Y Z", or similar.
argument-hint: "<company name>" <theme1> <theme2> ...
---

# Stock Fetcher

Download stock images from Unsplash into a folder named after the company.

## Tool location

```
/Users/laurihynonen/Projects/stock-fetcher
```

## Run command

```bash
cd /Users/laurihynonen/Projects/stock-fetcher && npm run fetch -- "<company>" "<theme1>" "<theme2>" "<theme3>" --count 10
```

## Workflow

1. **Get company name and themes** — from `$ARGUMENTS` or ask the user. If the user hasn't specified themes, infer 3–5 good search queries from the company name/industry.
2. **Run the fetcher:**
   ```bash
   cd /Users/laurihynonen/Projects/stock-fetcher && npm run fetch -- "<company>" "<theme1>" "<theme2>" --count 10
   ```
3. **Report the output folder** — images land in `~/Pictures/stock/<company-slug>/`

## Options

| Flag | Default | Purpose |
|---|---|---|
| `--count <n>` | 10 | Total images to download |
| `--out <dir>` | `~/Pictures/stock` | Root output directory |

## Theme guidance

Images are split evenly across themes. 3 themes + 10 images = ~3–4 per theme. Choose themes that are:
- Specific enough to get relevant results ("modern Nordic office" beats "office")
- Varied so the set has diversity (don't use 3 near-identical queries)

If the user just says the company name/type, infer themes yourself — don't ask.

## API key

Stored in `/Users/laurihynonen/Projects/stock-fetcher/.env` — already configured.
