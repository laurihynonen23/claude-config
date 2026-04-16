---
name: potential_clients_software
description: Finnish Website Rebuild Lead Finder — modular pipeline for finding Finnish B2B companies with outdated websites
type: project
---

Lead-generation and qualification tool for a website redesign agency. At `/Users/laurihynonen/potential_clients_software`.

**Why:** Find Finnish SMB companies that have money but weak websites — ranked by budget, site pain, sales fit, and delivery risk.

**Stack:** Python 3.12, FastAPI, SQLModel/SQLite, Playwright, BS4, Streamlit, Anthropic/OpenAI/mock LLM. CLI via Typer (`leads` command).

**Key facts:**
- PRH API is v3 at `https://avoindata.prh.fi/opendata-ytj-api/v3/companies` (not the old `/bis/v1`)
- PRH does NOT return website URLs in search results — heuristic domain guessing is the main website discovery mechanism
- PRH `mainBusinessLine` filter is loose; must post-filter results by TOL code prefix in Python
- TOL letter groups (C=Manufacturing) map to 2-digit numeric prefixes (10–33)
- Municipality filter uses 3-digit codes (Tampere=837, Helsinki=091)
- SQLModel sessions must be closed before asyncio.run() — extract primitive values (IDs, URLs) before session closes

**How to apply:** When resuming work, check pipeline status with `leads status`, use `--no-playwright` for fast local crawls, set `LLM_PROVIDER=anthropic` + API key to get real AI evaluations.
