---
name: design-agent-loops
description: Design, critique, and implement reliable AI agent loops for software, research, content, operations, data, and other repeatable project work. Use when the user asks for loop engineering, autonomous or recurring agent workflows, self-correcting agents, maker-checker systems, multi-agent orchestration, project automation ideas, persistent agent memory, verification gates, stop conditions, or ways Claude Code or Codex can repeatedly work toward a verified outcome. Also use when inspecting a project to suggest high-value loops. Do not use for visual/video animation loops; use the relevant media skill instead.
---

# Design Agent Loops

Design feedback systems that move from a goal to a verified outcome with bounded autonomy. Prefer a small closed loop with strong checks over an impressive but untestable agent fleet.

## Choose the mode

- **Suggest:** Inspect the project or workflow and rank useful loop ideas.
- **Design:** Turn one goal into a complete loop specification.
- **Critique:** Find missing gates, unsafe actions, weak memory, runaway costs, or false completion signals in an existing loop.
- **Implement:** Create the smallest cross-platform artifacts needed to run the loop in Claude Code and Codex.

If the user is broad, start in Suggest mode. If they name a goal, start in Design mode. Do not implement files, schedules, hooks, or external actions unless requested or clearly implied.

If there is no inspectable project and the user provided no workflow context, ask one focused question: which project or repeated workflow should the loop improve? Do not conduct a long intake interview.

## Inspect before proposing

Gather only the context needed to understand:

1. Repeated work, bottlenecks, and handoffs.
2. Existing commands, tests, linters, schemas, checklists, CI, and source-of-truth documents.
3. Available agent primitives: automations, subagents, worktrees, skills, connectors, and durable storage.
4. Risky or irreversible actions.
5. Existing `graphify-out/graph.json`; when present, query it before broadly re-reading a large repository.

Do not assume a harness supports a named command. Inspect the available Claude Code or Codex capabilities and adapt the design to what actually exists.

## Find good loop candidates

Look for work that is frequent, expensive, measurable, and reversible. Strong candidates have:

- a precise goal;
- machine-checkable or rubric-based feedback;
- bounded actions;
- durable state;
- enough repetition to repay setup cost;
- a clear owner when escalation is needed.

Reject or keep human-led tasks that are rare, politically sensitive, irreversible, poorly specified, or impossible to verify independently.

Score each candidate from 1 to 5:

| Factor | Question |
|---|---|
| Value | How much useful work or risk reduction does one successful run create? |
| Frequency | How often will this run? |
| Verifiability | Can completion be checked objectively? |
| Safety | Can failures be contained and reversed? |
| Cost efficiency | Is the expected value worth model, tool, and review cost? |

Rank with:

`priority = value + frequency + verifiability + safety + cost efficiency`

Treat any candidate with `verifiability <= 2` or `safety <= 2` as advisory-only until better gates exist.

For a broader pattern catalog, read [references/pattern-library.md](references/pattern-library.md).

## Design the loop

Use this sequence:

1. **Discover:** Load durable context, current state, constraints, and new evidence.
2. **Plan:** Select the smallest next action that moves a measurable condition.
3. **Execute:** Perform bounded work in an isolated environment when edits may conflict.
4. **Verify:** Check the result against tests, schemas, source evidence, or an explicit rubric.
5. **Iterate:** Feed structured failure information into the next attempt.

Every design must define:

- **Goal:** One outcome, not a vague activity.
- **Done condition:** Observable evidence that ends the loop.
- **Trigger:** Manual, event-driven, scheduled, or continuous.
- **Inputs:** Authoritative context and freshness requirements.
- **Actions:** Allowed tools, scope, and side effects.
- **Verifier:** Deterministic checks first; independent reviewer second.
- **Memory:** Durable state that survives sessions.
- **Budgets:** Maximum iterations, time, tokens/cost, and parallel workers.
- **Escalation:** Conditions requiring a human.
- **Failure handling:** Retryable, blocked, unsafe, and partial-success states.

## Pick the topology

Use a **single-agent loop** when one bounded task has strong deterministic feedback. This is the default.

Use a **maker-checker loop** when quality needs judgment. Keep the checker independent: give it the goal, rubric, and artifact, not the maker's reasoning.

Use a **fleet loop** only when work can be cleanly partitioned and parallelism repays coordination cost. Give each worker separate ownership, preferably an isolated worktree, and let the orchestrator integrate results.

Never add agents merely to make the design look sophisticated.

## Design memory

Persist facts, not chat transcripts. Keep:

- current objective and status;
- last verified checkpoint;
- attempts and structured failure reasons;
- decisions and constraints;
- unresolved blockers;
- artifact and evidence links;
- next eligible action.

For implemented project loops, default to:

```text
.agent-loops/<loop-name>/
├── LOOP.md       versioned loop contract and rubric
├── STATE.md      compact current checkpoint
└── runs/         timestamped run summaries and evidence
```

Use existing project systems instead when they are already authoritative, such as an issue tracker, database, CI, or Graphify knowledge graph. Do not duplicate source-of-truth data into memory.

## Build verification gates

Prefer gates in this order:

1. Deterministic: tests, type checks, linters, schemas, queries, diffs, budgets.
2. Evidence-backed: citations, screenshots, logs, benchmark results.
3. Independent rubric review by a fresh agent.
4. Human approval for ambiguous, costly, public, privileged, or irreversible actions.

Do not let the agent that produced an artifact declare success solely from its own narrative. A loop without a trustworthy gate is repeated generation, not reliable automation.

## Bound autonomy

Always set:

- a hard iteration limit;
- a time or cost budget;
- a no-progress detector;
- a maximum repeated failure count;
- an approval gate before destructive or external actions;
- a terminal state: `passed`, `blocked`, `budget_exhausted`, or `needs_human`.

Default recommendation when no data exists: 3 iterations, one worker, and escalation after the same failure occurs twice. Explain that this is an initial operating point, not a universal optimum.

## Output

For Suggest mode, return:

1. A ranked table of 3-5 candidates with outcome, trigger, verification gate, topology, effort, and score.
2. Why the top candidate is suitable.
3. The smallest pilot version.
4. What must remain human-controlled.

For Design mode, use:

```markdown
# Loop: <name>

## Outcome
- Goal:
- Done when:
- Non-goals:

## Control
- Trigger:
- Owner:
- Max iterations:
- Time/cost budget:
- Escalate when:

## Context and memory
- Read:
- Persist:
- Freshness rule:

## Cycle
1. Discover:
2. Plan:
3. Execute:
4. Verify:
5. Iterate:

## Verification gates
- Deterministic:
- Independent review:
- Human approval:

## Failure states
- Retryable:
- Blocked:
- Unsafe:

## Platform mapping
- Shared artifacts:
- Claude Code:
- Codex:

## Pilot
- First narrow run:
- Evidence to collect:
- Expansion condition:
```

Include concrete commands and paths only after inspecting the project.

## Implement portably

Keep the loop contract and memory platform-neutral. Put harness-specific adapters around the shared design:

- Claude Code: skill/instructions, available hooks or scheduling, subagents, and worktrees.
- Codex: skill/instructions, available automations or goals, subagents, and worktrees.

If a platform lacks a required primitive, degrade to a manual trigger or script rather than inventing support. Keep credentials and machine-specific paths out of committed files.

After implementation, run one narrow dry run. Verify the stop condition, memory update, failure path, and cost controls before scheduling or widening scope.

## Hard rules

1. Start closed; open autonomy only after gates prove reliable.
2. Separate maker and checker when verification is subjective.
3. Make state durable and compact.
4. Bound iterations, spend, scope, and side effects.
5. Escalate uncertainty instead of silently lowering the standard.
6. Optimize for verified outcomes, not agent activity.
