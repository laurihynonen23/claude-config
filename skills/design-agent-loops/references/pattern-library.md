# Agent Loop Pattern Library

Use these patterns as starting points. Adapt gates and side effects to the actual project.

## Coding

### Test-to-green loop

- Trigger: failing test, CI event, or manual issue selection
- Goal: make a named failing check pass without unrelated regressions
- Action: reproduce, isolate, patch, run focused tests, run broader checks
- Gate: original failure passes and required regression suite stays green
- Memory: failing command, root cause, changed files, test evidence
- Stop: pass, repeated same failure twice, or scope exceeds the issue

### Dependency update loop

- Trigger: scheduled update window or security alert
- Goal: update one dependency while preserving behavior
- Action: inspect changelog, update lockfile, migrate APIs, run tests
- Gate: build, tests, vulnerability scan, and bounded diff
- Human gate: major versions, license changes, or production rollout

### Backlog implementation loop

- Trigger: approved issue with acceptance criteria
- Goal: complete one issue and produce reviewable evidence
- Action: plan, implement in isolated branch/worktree, test, self-review
- Gate: acceptance checks plus independent code review
- Stop: PR ready, blocked by missing product decision, or budget reached

### Maintenance scout loop

- Trigger: weekly schedule
- Goal: identify a small ranked set of actionable maintenance risks
- Action: inspect CI, TODOs, stale dependencies, flaky tests, hot files
- Gate: each finding has evidence, impact, owner, and proposed next action
- Side effect: create drafts only; require approval before opening tickets

## Research

### Evidence synthesis loop

- Trigger: research question
- Goal: answer with sufficient current, primary-source evidence
- Action: search, extract claims, compare sources, resolve conflicts
- Gate: every material claim has a source and uncertainty is explicit
- Memory: query log, accepted/rejected sources, unresolved conflicts
- Stop: confidence threshold met or evidence remains contradictory

### Monitoring loop

- Trigger: schedule or new-source event
- Goal: detect meaningful changes since the last checkpoint
- Action: fetch authoritative sources, diff facts, classify significance
- Gate: change is dated, sourced, non-duplicate, and relevant
- Stop: report only new material; persist the new checkpoint

## Content

### Draft-critique-rewrite loop

- Trigger: approved brief
- Goal: produce content that clears a measurable editorial rubric
- Action: draft, independent critique, targeted rewrite
- Gate: factual checks plus rubric thresholds for audience, clarity, and voice
- Budget: cap rewrites; escalate conflicts in the brief

### Content refresh loop

- Trigger: age threshold, traffic decline, or product change
- Goal: update an existing asset without losing valid content
- Action: identify stale claims, research changes, edit, compare
- Gate: links work, claims are current, intent is preserved, diff is bounded
- Human gate: publishing

## Product and operations

### Feedback triage loop

- Trigger: new batch of support tickets, reviews, or interviews
- Goal: cluster evidence into ranked product problems
- Action: normalize, deduplicate, cluster, attach representative evidence
- Gate: every theme has frequency, severity, examples, and confidence
- Human gate: roadmap decisions

### Incident follow-up loop

- Trigger: resolved incident
- Goal: produce a complete, evidence-backed follow-up package
- Action: assemble timeline, detect gaps, draft actions, assign owners
- Gate: timeline links to logs/events and every action has owner/due date
- Human gate: blame-sensitive conclusions and external communication

### Sales qualification loop

- Trigger: new lead
- Goal: decide whether a lead meets explicit qualification criteria
- Action: enrich, score, identify missing information, draft outreach
- Gate: required fields present and score rationale cites source data
- Human gate: send external messages until the system is proven

## Data

### Data quality repair loop

- Trigger: failed validation or anomaly
- Goal: restore a dataset to declared quality thresholds
- Action: isolate affected partition, diagnose, propose or apply reversible fix
- Gate: schema, completeness, uniqueness, freshness, and reconciliation checks
- Human gate: destructive backfills or source-system changes

### Experiment analysis loop

- Trigger: experiment reaches analysis threshold
- Goal: produce a reproducible decision package
- Action: validate assignment, calculate metrics, test sensitivity, summarize
- Gate: preregistered metrics, sample checks, reproducible query/notebook
- Human gate: product decision

## Choosing among patterns

Prefer candidates where existing feedback already exists. A failing CI command is a stronger foundation than a vague instruction to "improve quality."

Combine patterns only after each works independently. For example, prove the maintenance scout before allowing it to open issues, and prove issue implementation before chaining the two.

Avoid scheduling a loop until a manual dry run demonstrates:

1. Correct context loading.
2. A trustworthy pass/fail gate.
3. Durable checkpoint updates.
4. Bounded retries and cost.
5. Safe behavior on missing permissions or ambiguous input.
