---
name: reference-website
description: Build beautiful, coherent websites from reference code, screenshots, or existing files. Use this skill whenever the user says "build a site like this", "use this as reference", "make it look like X", shares screenshots or code to base a design on, or wants to turn reference material into a working website. Also use when asked to extract a design system from existing code, merge multiple design references, or improve a UI's visual coherence. Always trigger this when references are provided alongside a website build request.
---

# Reference-Driven Website Building

**Core rule: references are input, not truth.** Extract what makes them good. Build something cleaner, more coherent, and more usable than the inputs.

## The problem this solves

Most reference-based builds fail by:
- Copying surface details without understanding structure
- Merging multiple references into an inconsistent Frankenstein UI
- Ignoring the target stack's conventions
- Making things "prettier" while reducing clarity

## Workflow checklist

Work through these in order. Don't start coding major changes until steps 1–3 are solid.

- [ ] **0. Gather inputs** — task, references, stack, constraints
- [ ] **1. Audit references** — extract and classify patterns
- [ ] **2. Choose direction** — pick one dominant reference, explain why
- [ ] **3. Define scope** — pages, sections, components, key paths
- [ ] **4. Structure** — IA, layout hierarchy, responsive priorities
- [ ] **5. Token system** — spacing, type, color, radius, shadow
- [ ] **6. Components** — anatomy, variants, states, edge cases
- [ ] **7. Validate** — usability, consistency, accessibility, performance
- [ ] **8. Hand off** — notes or production code

## Step 0 — Gather inputs

Ask only what's necessary. Make assumptions and state them.

Minimum: what to build, primary audience, what references exist, target stack, hard constraints (brand, a11y, existing components).

## Step 1 — Audit references

For each reference, label each pattern **Keep / Adapt / Avoid**:

- **Structure:** layout shells, grid rules, section order, nav style, hierarchy
- **Visual:** spacing rhythm, type scale, color, radius, shadows, motion
- **Interaction:** CTA treatment, hover/focus states, form behavior, feedback patterns
- **Code:** component organization, styling approach, token usage, existing primitives

## Step 2 — Choose direction

Never average multiple references equally. Pick one:
- **Primary** — drives layout, rhythm, component treatment
- **Secondary** — small accent influences only
- **Rejected** — explicitly called out and excluded

State why. One primary reference prevents visual dialects from mixing.

## Step 3 — Scope

List pages, sections, core components, top 1–3 user paths, and what's out of scope.

## Step 4 — Structure

For each page: purpose, section order, layout hierarchy, breakpoints.

- Start with content and actions, not decorative framing
- Primary CTA must be visible without interpretation
- Prefer strong sections over many weak sections
- Minimize nesting

## Step 5 — Token system

Don't invent tokens if existing ones can be extended.

**Spacing:** `0 4 8 12 16 24 32 48 64 96 128` — inside-group gaps smaller than between-group.

**Type scale:** `12 14 16 20 24 30 40` — body line-height 1.5–1.7. Prefer weight and contrast over adding more sizes.

**Color:** bg / surface / text-primary / text-secondary / border / one accent / semantic states. Keep neutral temperature consistent. Don't overuse the accent.

**Radius:** small system like `0 / 8 / 12 / 16 / 24`. **Elevation:** 3–5 levels — card / popover / sticky / modal / urgent. Motion only where it improves clarity.

## Step 6 — Components

For important components: purpose, anatomy, variants, states (default / hover / focus / active / disabled / loading / empty / error / success), responsive behavior, a11y notes, edge cases (long text, missing data, small screens, keyboard nav).

## Step 7 — Validate

**Usability:** Can a first-time user tell what the page is, where to look, what to do next?

**Consistency:** spacing rhythm, type hierarchy, accent usage, radius/shadow uniformity

**Accessibility:** contrast, focus visibility, semantic HTML, form labels, touch targets ≥44px, reduced motion

**Performance:** unnecessary nesting, expensive effects, fragile layout, gratuitous client-side complexity

## Step 8 — Hand off

Default output:
1. Working brief (user, goals, constraints, assumptions)
2. Reference analysis (per reference: strengths, weaknesses, keep/adapt/avoid)
3. Chosen direction + design principles
4. IA / page structure with section order and key paths
5. Component inventory
6. Design tokens as CSS variables or JSON
7. Page-level guidance (hierarchy, CTAs, responsive behavior)
8. States and edge cases
9. Implementation notes tied to the actual stack

If coding is requested: exact files to create/change, component architecture, implementation order, production-ready code or targeted patches.

## Non-negotiables

**Make the next action obvious** — every page must make clear at a glance: what it is, who it's for, primary action, secondary action, where nav is. Obvious over clever.

**One coherent design language** — unify spacing, type scale, radius, depth, accent usage. No mixed visual dialects.

**Respect the target stack** — Tailwind → stay idiomatic Tailwind. CSS modules → don't force utility classes. Existing tokens → extend before inventing. Existing primitives → compose before adding new systems.

**Structure before polish** — layout and hierarchy first. Beauty comes from clear structure, strong spacing, restrained type, coherent color, predictable interactions.

**Accessibility is quality** — keyboard use, zoomed layouts, small screens, reduced motion, color vision differences, loading states all count.

## Code generation rules

1. Inspect existing conventions first — reuse primitives before inventing new ones
2. Mobile-first responsiveness, preserve accessibility semantics
3. Don't rewrite the whole app unless necessary
4. Don't introduce a new styling system without reason
5. Don't copy reference code literally if it clashes with the target system

**Quality bar:** the result should feel cleaner, more coherent, easier to use, and simpler to maintain than the references.
