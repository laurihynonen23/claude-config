---
name: web-design-pipeline
description: Master orchestrator for website design and build work. Trigger when the user wants to build, redesign, or style a website, landing page, or UI — especially at session start. Recognizes what stage to enter based on inputs: URL reference → run reference-extractor first; screenshots or existing code as reference → start at reference-website; build from scratch or from a brief → go directly to frontend-design + ui-ux-pro-max. Coordinates all four design skills (reference-extractor, reference-website, frontend-design, ui-ux-pro-max) as a coherent pipeline.
---

# Web Design Pipeline

Orchestration guide for website design work. Read this at the start of any website build or redesign session to know which skills to engage and in what order.

## The four skills and what they do

| Skill | Role | When it runs |
|---|---|---|
| `reference-extractor` | Crawls a live URL and extracts cleaned HTML, CSS, screenshots, and a reference brief | First, when the user provides a reference URL |
| `reference-website` | Turns reference material into a structured design direction: keep/adapt/avoid analysis, token system, component inventory, implementation plan | Before coding, when any reference exists |
| `frontend-design` | Generates production-grade code with intentional aesthetic direction — avoids generic AI patterns | Code generation phase |
| `ui-ux-pro-max` | Searchable database of 67 styles, 96 palettes, 57 font pairings, 99 UX guidelines, accessibility rules | Consulted at any stage for specific design decisions |

## Entry point decision tree

Read the user's inputs and choose the right starting point:

### User gives a reference URL
→ Run `reference-extractor` on the URL first.
→ Hand the output (`notes/reference-brief.json`, `components/`, `cleaned/`) to `reference-website`.
→ Then proceed to `frontend-design`.

### User shares screenshots, existing code, or describes "make it look like X"
→ Skip extraction. Go directly to `reference-website`.
→ Audit the references, establish direction, produce the brief.
→ Then proceed to `frontend-design`.

### User wants to build from scratch (no references)
→ Go directly to `frontend-design`.
→ Consult `ui-ux-pro-max` for style, palette, and typography decisions before writing code.

### User asks a specific design question (palette, font, style, accessibility, UX)
→ Use `ui-ux-pro-max` directly. No need to run the full pipeline.

### User wants to improve or restyle an existing page
→ Treat existing code as reference material → `reference-website` to audit it.
→ Then `frontend-design` to implement improvements.
→ `ui-ux-pro-max` for any decisions about new styles or colors.

## Pipeline stages in order

### Stage 1 — Research (conditional)
**Skill:** `reference-extractor`
**Run when:** user provides a URL to reference.
**What to do:**
- Extract with `node dist/cli.js extract --url <URL> --out ./output` from `/Users/laurihynonen/Projects/reference-extractor`
- Report output path and key files to user
- Carry `notes/reference-brief.json` and `components/` into Stage 2

**Skip when:** user provides screenshots, code snippets, or no reference at all.

### Stage 2 — Direction (conditional)
**Skill:** `reference-website`
**Run when:** any reference material exists (URL output, screenshots, existing code).
**What to do:**
- Audit each reference: label patterns Keep / Adapt / Avoid
- Pick one dominant reference as primary
- Define token system: spacing, type scale, color, radius, shadow
- Produce component inventory and implementation scope
- Output: a written brief the coding phase can execute against

**Skip when:** building fully from scratch with no references.

### Stage 3 — Design decisions (ongoing)
**Skill:** `ui-ux-pro-max`
**Run at:** any point during Stage 2 or Stage 4 when making specific design decisions.
**Use it for:**
- Choosing a color palette for a product type or style
- Picking a font pairing that fits the aesthetic direction
- Verifying accessibility (contrast, touch targets, keyboard nav)
- Selecting a UI style (glassmorphism, brutalism, bento grid, etc.)
- Chart type recommendations
- UX anti-pattern checks

**Search command:**
```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>
# domains: style, color, typography, product, landing, chart, ux
# add --stack nextjs / react / vue / svelte / shadcn / etc.
```

### Stage 4 — Build
**Skill:** `frontend-design`
**Run when:** brief is ready (or no brief needed).
**What to do:**
- Commit to a clear aesthetic direction before writing any code
- Make bold, context-specific choices — no generic AI aesthetics
- Implement working, production-grade code
- Apply the token system from Stage 2 (if it exists)
- Reference `ui-ux-pro-max` for any remaining design decisions

## Passing context between stages

- Stage 1 → Stage 2: hand off `notes/reference-brief.json`, `components/`, and `cleaned/<page>/reference.html`
- Stage 2 → Stage 4: the written brief including chosen direction, token values, and component inventory
- Stage 3 → any stage: specific recommendations (palette name, font pair, style CSS keywords) to apply in the brief or code

## Key principles to enforce across all stages

**One design language.** Every element — spacing, color, radius, type scale, shadow — must come from the same system. No mixed visual dialects.

**Structure before polish.** Hierarchy and layout first. Beauty follows from clear structure, strong spacing, and coherent color. Never decorate before the skeleton is solid.

**Bold is better than generic.** A strong, unusual aesthetic executed well beats a safe, average one. Push toward a clear point of view.

**Accessibility is quality, not a checklist.** WCAG contrast, 44px touch targets, keyboard navigation, semantic HTML — these are quality criteria, not optional extras.

**Respect the stack.** Tailwind → idiomatic Tailwind. CSS modules → don't force utilities. Extend existing tokens before inventing new ones. Compose existing primitives before adding new systems.

## Quick reference — which skill for what

| Situation | Skill |
|---|---|
| "I want to build a site like [URL]" | reference-extractor → reference-website → frontend-design |
| "Here's a screenshot, build something like this" | reference-website → frontend-design |
| "Build me a landing page for X" | frontend-design (+ ui-ux-pro-max for palette/style) |
| "What color palette fits a music org?" | ui-ux-pro-max |
| "Restyle this component" | reference-website (audit current) → frontend-design |
| "Is this accessible?" | ui-ux-pro-max (ux domain) |
| "What font pairing should I use?" | ui-ux-pro-max (typography domain) |
