---
name: new-site-from-brief
description: Full pipeline orchestrator for building a new website from a kickoff brief. Trigger when the user provides an old site URL (content source), a reference site URL (design source), and optionally an assets folder and stack. Runs site-content-extractor, reference-extractor, extract-design, reference-website, ui-ux-pro-max, and frontend-design as a coherent pipeline. Also trigger on "build [company] site", "new site for [client]", "redesign [site]".
argument-hint: "<old-site-url> <reference-url> [assets-path] [stack]"
---

# New Site From Brief

Full orchestration pipeline for building a new website. Combines content extraction from the client's old site, layout and design token extraction from a reference site, and structured build using design direction and production-grade code generation.

**Every site built with this skill must be editor-ready.** The tvenda-style content editor must be able to read, edit, preview, and publish content without touching code. The editor contract below is mandatory on every build — no exceptions, no workspace dependency.

---

## Editor Contract (mandatory — applies globally)

### Required project structure

```
src/
  app/
    (site)/           ← public-facing routes only
    (editor)/         ← /login, /editor — the editor UI
    api/
      editor/         ← draft, publish, auth, upload routes
  content/
    schema.ts         ← zod schemas for all section types
    server.ts         ← server-only content loaders
    config.ts         ← PAGE_DEFINITIONS, constants, site config
    site.json         ← global editable settings (nav, footer, theme, contacts)
    fi/               ← one JSON file per page per locale
      home.json
    en/
      home.json
  editor/
    lib/              ← editor business logic (draft, publish, auth)
.editor-data/         ← runtime drafts, sessions, history (gitignored)
public/
  uploads/editor/     ← uploaded assets (gitignored)
```

### schema.ts — conventions

```ts
import { z } from 'zod'

export const localeSchema = z.enum(['fi', 'en'])
export type Locale = z.infer<typeof localeSchema>

export const pageKeySchema = z.enum(['home', 'services', /* pages in scope */])
export type PageKey = z.infer<typeof pageKeySchema>

// Every section must have id + visible
const sectionBaseSchema = z.object({
  id: z.string(),
  visible: z.boolean().default(true),
})

// type is ALWAYS a literal, never a plain string
const heroSectionSchema = sectionBaseSchema.extend({
  type: z.literal('hero'),
  title: z.string(),
  subtitle: z.string(),
})

// Repeatable items also need stable ids
const teamMemberSchema = z.object({
  id: z.string(),
  name: z.string(),
  title: z.string(),
})

// Discriminated union — editor uses this to know what fields to show
export const pageSectionSchema = z.discriminatedUnion('type', [
  heroSectionSchema,
  // all section schemas
])
export type PageSection = z.infer<typeof pageSectionSchema>

export const pageContentSchema = z.object({
  key: pageKeySchema,
  locale: localeSchema,
  route: z.string(),
  metadata: z.object({ title: z.string(), description: z.string() }),
  sections: z.array(pageSectionSchema),
})
export type PageContent = z.infer<typeof pageContentSchema>

export const siteSettingsSchema = z.object({
  siteId: z.literal('CLIENT_ID'),  // unique per project
  name: z.string(),
  defaultLocale: localeSchema,
  theme: themeTokensSchema,
  navLinks: z.array(z.object({ id: z.string(), label: z.string(), href: z.string() })),
  footerLinks: z.array(z.object({ id: z.string(), label: z.string(), href: z.string() })),
  editor: z.object({
    supportedLocales: z.array(localeSchema),
    supportedPageKeys: z.array(pageKeySchema),
    supportedSectionTypes: z.array(z.string()),
  }),
})

export const contentBundleSchema = z.object({
  site: siteSettingsSchema,
  locales: z.object({
    fi: z.object({ home: pageContentSchema.optional() /* ... */ }),
    en: z.object({ home: pageContentSchema.optional() /* ... */ }),
  }),
})
```

### server.ts — content loaders

```ts
import 'server-only'
import { promises as fs } from 'fs'
import path from 'path'
import { cookies } from 'next/headers'
import { ACTIVE_PREVIEW_COOKIE, CONTENT_ROOT, DRAFT_ROOT, PAGE_DEFINITIONS } from '@/content/config'
import { pageContentSchema, siteSettingsSchema, contentBundleSchema } from '@/content/schema'

function contentPath(...parts: string[]) {
  return path.join(process.cwd(), CONTENT_ROOT, ...parts)
}

export async function loadPublishedBundle() {
  const site = siteSettingsSchema.parse(JSON.parse(await fs.readFile(contentPath('site.json'), 'utf-8')))
  const locales: Record<string, Record<string, unknown>> = { fi: {}, en: {} }
  for (const def of PAGE_DEFINITIONS) {
    const raw = await fs.readFile(contentPath(def.locale, def.fileName), 'utf-8')
    locales[def.locale][def.key] = pageContentSchema.parse(JSON.parse(raw))
  }
  return contentBundleSchema.parse({ site, locales })
}

export async function loadActiveBundle() {
  const cookieStore = await cookies()
  const draftId = cookieStore.get(ACTIVE_PREVIEW_COOKIE)?.value
  if (!draftId) return loadPublishedBundle()
  try {
    const raw = await fs.readFile(path.join(process.cwd(), DRAFT_ROOT, 'drafts', `${draftId}.json`), 'utf-8')
    return contentBundleSchema.parse(JSON.parse(raw).bundle)
  } catch {
    return loadPublishedBundle()
  }
}

export async function getPageContent(locale: Locale, key: PageKey) {
  const bundle = await loadActiveBundle()
  const page = bundle.locales[locale]?.[key]
  if (!page) throw new Error(`Missing page content for ${locale}:${key}`)
  return page
}
```

### config.ts — page registry

```ts
export const CONTENT_ROOT = 'src/content'
export const DRAFT_ROOT = '.editor-data'
export const ACTIVE_PREVIEW_COOKIE = 'SITEID_editor_preview_draft'
export const EDITOR_SESSION_COOKIE = 'SITEID_editor_session'

export const PAGE_DEFINITIONS = [
  { key: 'home', locale: 'fi', label: 'Etusivu', route: '/', fileName: 'home.json' },
  // one entry per page per locale
]
```

### Route files — renderers only, never content containers

```ts
// src/app/(site)/page.tsx
import { getPageContent } from '@/content/server'
import { HeroSection } from '@/components/sections/HeroSection'

export default async function HomePage() {
  const page = await getPageContent('fi', 'home')
  return (
    <>
      {page.sections.filter(s => s.visible).map(section => {
        if (section.type === 'hero') return <HeroSection key={section.id} {...section} />
      })}
    </>
  )
}
```

Never hardcode content in route files.

### Section components — typed props from schema

```ts
import type { PageSection } from '@/content/schema'
type Props = Extract<PageSection, { type: 'hero' }>

export function HeroSection({ title, subtitle }: Props) {
  return <section><h1>{title}</h1><p>{subtitle}</p></section>
}
```

### Content JSON rules

- `id` on every section: kebab-case, stable, never change after shipping
- `id` on every repeatable item (cards, team members, etc.)
- `type` must exactly match the literal in schema.ts
- `visible` always included

### .gitignore additions

```
.editor-data/
public/uploads/editor/
```

### Editor contract checklist (complete before Phase 3 handoff)

1. Define all section types in `schema.ts` before writing any components
2. Create `site.json` with global settings, set `siteId` to unique client ID
3. Create `{locale}/{page}.json` for every editable route
4. Write section components with typed props from schema
5. Route files call `getPageContent`, render section components — no hardcoded copy
6. Update `PAGE_DEFINITIONS` with every editable route + locale
7. `supportedSectionTypes` in site.json matches all type literals in schema
8. `npm run build` passes

---

## Kickoff prompt format

The user gives you one prompt in this shape:

```
Build [Company X] website.
- Old site (content): https://companyx.com
- Design reference: https://websitey.com
- Assets: /path/to/folder/
- Stack: Next.js + Tailwind
```

Any subset is valid — old site and reference are the minimum. If assets or stack are missing, ask in plan mode.

---

## Phase 0 — Plan mode (always run first)

Enter plan mode immediately. Ask only what you can't infer and that will change decisions. Batch all questions into one message.

**Questions to ask:**

1. **Pages** — which pages does the site need? (e.g. Home, About, Services, Contact, Blog)
2. **Reference fidelity** — close copy of the reference site's design, or just borrow the vibe/structure?
3. **Style direction** — any adjustments on top of the reference? (darker, lighter, different accent color, more minimal, bolder type, etc.)
4. **Assets** — how should the provided images/videos be used? (hero, backgrounds, section visuals, gallery, scattered)
5. **Stack** — if not provided: Next.js + Tailwind assumed, confirm or correct
6. **Content gaps** — is there content the old site doesn't have that needs to be written from scratch?

Do not ask about things you can discover by running the extractors.

---

## Phase 1 — Parallel extraction (run all four simultaneously)

Start extractions immediately — don't wait for plan mode answers to come back. Run in parallel.

### 1a — Content: `site-content-extractor`

```bash
cd ~/site-content-extractor && npm run dev -- crawl --url <OLD_SITE_URL> --out ./output
```

Key outputs:
- `AGENT_CONTEXT.md` — global nav, footer, contact, full page inventory
- `pages/<slug>/page.md` — per-page copy (nav/footer stripped)
- `global/navigation.md`, `global/footer.md` — shared elements

### 1b — Layout reference: `reference-extractor`

```bash
cd ~/Projects/reference-extractor && node dist/cli.js extract --url <REFERENCE_URL> --out ./output
```

Key outputs:
- `notes/reference-brief.json` — compact site overview
- `components/` — shared patterns (header, footer, cards)
- `cleaned/<page-id>/reference.html` + `reference.css`
- `sections/<page-id>/` — per-section HTML, CSS, screenshot

### 1c — Design tokens: `extract-design`

```bash
npx designlang <REFERENCE_URL> --screenshots
```

Key outputs (in `design-extract-output/`):
- `*-design-language.md` — full design system description for LLMs
- `*-tailwind.config.js` — ready-to-use Tailwind theme
- `*-variables.css` — CSS custom properties
- `*-shadcn-theme.css` — shadcn/ui theme (if stack uses shadcn)
- `*-preview.html` — visual swatch overview

### 1d — Client assets: `client-asset-scraper` (run when old site URL provided)

Run `client-asset-scraper` on the old site URL to extract logo and key images.

Output lands in `~/Pictures/client-assets/<company-slug>/`. Use this folder as the primary asset source in Phase 3 before reaching for stock photos.

Skip this step only if the brief explicitly provides an assets folder — in that case, use what was provided.

### 1e — Stock photos: `stock-fetcher` (run when no provided assets and client assets are sparse)

If the brief has no assets folder AND the client-asset-scraper found fewer than 3 useful images, run stock-fetcher immediately:

```bash
cd ~/Projects/stock-fetcher && npm run fetch -- "<company>" "<theme1>" "<theme2>" "<theme3>" --count 15
```

Infer 3–5 themes from the company name and industry without waiting for plan mode. Good theme patterns:
- Company type: "modern architecture studio", "artisan bakery", "B2B software"
- Page needs: "professional team workspace", "product hero minimal"
- Aesthetic direction: inferred from reference site vibe

Output lands in `~/Pictures/stock/<company-slug>/`. Report the folder in plan mode so the user knows what's available.

---

## Phase 2 — Design direction

Once extractions complete and plan mode answers are in, run these in order.

### 2a — `reference-website` (audit + brief)

Feed it:
- `reference-extractor` output: `notes/reference-brief.json`, `components/`, `cleaned/`
- `extract-design` output: `*-design-language.md`, token files
- Plan mode answers about reference fidelity and style direction

Produce:
- Keep / Adapt / Avoid analysis of the reference site
- Chosen dominant direction (layout, rhythm, component treatment)
- Token system: spacing scale, type scale, color palette, radius, shadow
- Component inventory for the pages in scope
- Written brief the build phase executes against

### 2b — `ui-ux-pro-max` (design decisions)

Use to validate or choose:
- Color palette that fits the company type and style direction
- Font pairing that matches the aesthetic
- WCAG contrast check on the chosen palette
- UI style classification (if the user wants a named style applied on top of the reference)

```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>
# domains: style, color, typography, ux, product, landing
```

Run proactively for palette and typography. Run on demand for specific UX questions.

---

## Phase 3 — Build: `frontend-design`

Use the full brief from Phase 2. Apply:
- **Content** from site-content-extractor (X's copy, nav structure, page inventory)
- **Layout and structure** from reference-extractor (Y's section order, component patterns)
- **Token system** from extract-design + reference-website (colors, type, spacing, radius)
- **Assets** placed as agreed in plan mode

Rules from `frontend-design`:
- Commit to a clear aesthetic direction before writing any code
- Bold, context-specific choices — no generic AI aesthetics
- Token system applied consistently across every element
- Mobile-first, production-grade, accessible
- Structure and hierarchy first — polish follows

**Before writing any component code**, complete the editor contract scaffold:
1. Define all section schemas in `src/content/schema.ts`
2. Create `src/content/config.ts` with `PAGE_DEFINITIONS` and constants
3. Create `src/content/server.ts` with `loadActiveBundle` / `getPageContent`
4. Create `src/content/site.json` with global settings
5. Create `src/content/{locale}/{page}.json` for every route in scope
6. Only then write section components and route files

Route files render — they never contain copy. All copy lives in JSON content files.

---

## Asset handling

### Source priority

1. **User-provided assets folder** (brief) — use as-is
2. **Client assets** (`~/Pictures/client-assets/<slug>/`) — scraped from old site in Phase 1d
3. **Stock photos** (`~/Pictures/stock/<slug>/`) — fetched in Phase 1e when above are sparse
4. **None** — proceed without images; add placeholder comments in code

### Placement defaults

| Asset type | Default placement |
|---|---|
| Logo (SVG/PNG from client-asset-scraper) | Nav header + footer |
| Hero image/video | Full-width hero section on home page |
| og:image from old site | Hero or about section fallback |
| Product/service images | Relevant section visuals |
| Team photos | About page |
| Video (brand/promo) | Hero or dedicated section with autoplay muted |
| Gallery / portfolio | Dedicated grid section |
| Stock photos | Fill gaps where client assets are missing |

Override with plan mode answers. If user hasn't specified, ask in Phase 0.

Assets stay at their scraped/fetched path. Reference them relatively from the project root or ask user where to copy them.

---

## Context handoff between phases

| From | To | What to carry |
|---|---|---|
| site-content-extractor | Phase 3 | `AGENT_CONTEXT.md`, per-page `page.md` files, `global/` |
| reference-extractor | reference-website | `notes/reference-brief.json`, `components/`, `cleaned/<page>/` |
| extract-design | reference-website + Phase 3 | `*-design-language.md`, `*-tailwind.config.js`, `*-variables.css` |
| client-asset-scraper | Phase 3 | `~/Pictures/client-assets/<slug>/` manifest — logo path, hero path, key visuals |
| stock-fetcher | Phase 3 | `~/Pictures/stock/<slug>/` — which images to use where |
| reference-website | Phase 3 | Written brief: direction, token values, component inventory |
| ui-ux-pro-max | reference-website + Phase 3 | Palette name/hex values, font pair, style CSS keywords |
| Plan mode | All phases | Pages in scope, style adjustments, asset placement, stack |

---

## Phase 4 — Polish: `impeccable`

After Phase 3 is complete and the build compiles, run `/impeccable polish` on the site.

Impeccable requires two files at the project root:

- **PRODUCT.md** — brand, tone, users, strategic principles. Write this from the content and plan mode context (company name, industry, reference site vibe, style direction chosen in Phase 2).
- **DESIGN.md** — colors, typography, spacing, components. Write this from the extract-design output (`*-design-language.md` + token values from reference-website brief).

Create both files before invoking impeccable. Then:

```bash
node ~/.claude/skills/impeccable/scripts/load-context.mjs
```

Load `~/.claude/skills/impeccable/reference/polish.md` and apply it. Focus on:
- Visual hierarchy and spacing consistency
- Typography execution (scale, weight, line-height)
- Color application against the chosen palette
- Motion and interaction micro-details
- Mobile breakpoints

After polish, optionally run `/impeccable audit` if the user wants a formal quality check before handoff.

---

## Minimum viable kickoff

If the user gives only an old site and a reference with no other context, assume:
- Pages: whatever the old site has
- Reference fidelity: borrow the vibe, adapt to fit the company
- Stack: Next.js + Tailwind
- Assets: none (skip asset placement)

State assumptions in plan mode and proceed.
