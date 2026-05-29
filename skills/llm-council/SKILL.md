---
name: llm-council
description: Use when the user says "/llm-council", "council", "convene the council", "get the council's opinion", "council review", "council advice", or wants multi-perspective deliberation on a question, decision, design, or piece of work. Spawns multiple Claude subagents as distinct personas, has them critique each other anonymously, then a Chairman synthesizes a final answer. Adaptation of Karpathy's llm-council (https://github.com/karpathy/llm-council) for Claude Code — uses parallel sub-agents instead of multi-provider APIs.
---

# LLM Council

Convene a council of Claude subagents to deliberate on a hard question and return a synthesized verdict. Three stages: independent answers → anonymized peer review → chairman synthesis.

This is Karpathy's `llm-council` pattern adapted for Claude Code. Since all members are Claude, diversity comes from **persona prompts**, not different model providers. No external APIs.

## When to invoke

Trigger phrases:
- `/llm-council <question>`
- "convene the council on …"
- "get council opinion on …"
- "council review this …"
- "I want the best advice on …"

Good fits: architecture decisions, ambiguous design tradeoffs, code review on contentious changes, strategic product calls, hard debugging where one perspective keeps missing the bug, evaluating user's own writing or plan.

Bad fits: trivial questions, lookups with one correct answer, anything where a single agent suffices. If the question is simple, say so and answer directly — do **not** burn 5 subagents on "what's the syntax for X".

## The five council members

Each is a Claude subagent (spawned via the Agent tool, `subagent_type: general-purpose`) given a distinct persona system-prompt. Use these five by default. Adjust the roster only if the topic clearly demands it (e.g., add a "Security Auditor" for crypto questions).

1. **Pragmatist** — ships things. Optimizes for "good enough today over perfect next quarter." Asks: what's the smallest thing that works? What does this look like in production at 3am?
2. **Skeptic** — devil's advocate. Hunts failure modes, edge cases, hidden assumptions. Asks: how does this break? What is the user not telling us? What would I regret in six months?
3. **Architect** — systems thinker. Cares about coupling, invariants, long-term shape. Asks: what does this look like at 10×? Where do the seams go? What are we locking ourselves into?
4. **Researcher** — evidence-driven. Cites docs, RFCs, known incidents, named patterns. Asks: has someone solved this before? What do the actual specs say? Where is the closest prior art?
5. **Contrarian** — questions the framing. Asks: is this the right question? Is there a meta-level the user isn't seeing? What if the opposite is true?

The **Chairman** is a sixth agent, spawned only after the first two stages complete. Persona: senior decision-maker. Reads everything, weighs disagreements, picks a verdict.

## Stages

### Stage 1 — Independent responses (parallel)

Spawn all five council members **in one message** with parallel Agent tool calls. Each receives:
- The exact user question (verbatim — do not paraphrase).
- Their persona definition (above).
- Instructions: respond in your role, do not hedge to the median, length budget 400–600 words, no preamble, end with a one-line "Bottom line:" verdict.

Each member writes independently. They do not see each other yet.

### Stage 2 — Anonymized peer review (parallel)

Collect the five Stage-1 responses. **Strip identity** — relabel as "Member A", "Member B", … "Member E" in a shuffled order so the persona names don't leak. Save the shuffle mapping (you will need it at the end).

Spawn five reviewer agents **in one message** (parallel). Each reviewer gets:
- The original user question.
- All five anonymized responses (A–E).
- Instructions: rank A–E from best to worst on **accuracy** and **insight** (two separate rankings). For each, give a one-sentence justification. Then write one paragraph: "What the council collectively missed."

The reviewer's own (anonymized) answer is in the set — that is fine; Karpathy's design relies on this. Do not tell the reviewer which one is theirs.

### Stage 3 — Chairman synthesis (single agent)

Spawn one Chairman agent. It receives:
- The original user question.
- All five initial responses (still anonymized A–E, with personas now revealed in a separate "Member key" block so the Chairman knows who said what).
- All five peer reviews.
- Instructions: produce one final answer the user can act on. Do not enumerate the council. Resolve disagreements explicitly: name the strongest counter-argument and say why you overruled it. End with a "Decision:" line and a "Watch-outs:" line (2–3 bullets).

Chairman length budget: 500–800 words.

## Output to the user

Present in this exact structure:

```
# Council Verdict

## Decision
<Chairman's decision line, verbatim>

## Why
<Chairman's reasoning, ~400 words>

## Dissent worth keeping
<The strongest counter-argument the Chairman overruled, 2-4 sentences>

## Watch-outs
- <bullet>
- <bullet>
- <bullet>

---

<details>
<summary>Show the deliberation (5 members + peer review)</summary>

### Member responses
**Pragmatist:** <response>
**Skeptic:** <response>
**Architect:** <response>
**Researcher:** <response>
**Contrarian:** <response>

### Peer review consensus
<2-3 sentence summary of where reviewers agreed/disagreed on rankings, and what they said the council collectively missed>

</details>
```

The user usually only reads the top half. The collapsible keeps the receipts available without burying the verdict.

## Hard rules

1. **Spawn in parallel, not sequentially.** Stage 1: all five Agent calls in a single assistant message. Stage 2: all five reviewer Agent calls in a single assistant message. Sequential spawning wastes the user's time — there is no dependency between members within a stage.
2. **Persona system prompts are not optional.** Without them every agent converges to the same Claude-default answer and the council is theatre. Lead each agent's prompt with: "You are the [PERSONA NAME] on a council deliberating a user's question. Your role: [persona description from above]. Do not break character. Do not hedge to consensus."
3. **Pass the user's question verbatim.** No summarizing, no "the user is asking about X" — agents see the raw question.
4. **Anonymize in Stage 2.** Shuffle order. Strip persona labels. Use Member A–E only. The bias-reduction is the whole point of peer review.
5. **Do not run a second round.** Karpathy's design is one pass. If the Chairman's answer is wrong, the user iterates by asking a follow-up question — they do not ask for "council round 2".
6. **Skip the council for trivial questions.** If the question has one obvious correct answer, answer it directly and tell the user the council was overkill for this one. Do not burn 11 subagents on "should I use `let` or `const`".
7. **Budget the user's tokens.** This skill spawns 11 agents (5 + 5 + 1). That is expensive. Mention the cost framing once at the start: "Convening the council — this spawns 11 subagents in parallel." Then proceed.

## Agent prompt templates

### Stage 1 prompt (per member)

```
You are the {PERSONA_NAME} on a five-member council deliberating a user's question. Your role: {PERSONA_DESCRIPTION_FROM_ROSTER}.

Do not break character. Do not hedge to consensus — your job is to bring *this* perspective, not a balanced one. The other members bring the balance.

User's question (verbatim):
---
{USER_QUESTION}
---

Respond in 400-600 words. No preamble, no "Great question". End with a single line:
Bottom line: <your one-sentence verdict>
```

### Stage 2 prompt (per reviewer)

```
You are reviewing the responses of a five-member council to a user's question. You yourself were one of the five members, but the responses below are anonymized — you do not know which one is yours, and that is intentional. Judge on the merits.

User's question:
---
{USER_QUESTION}
---

The five responses (anonymized, shuffled):

Member A:
{RESPONSE_A}

Member B:
{RESPONSE_B}

Member C:
{RESPONSE_C}

Member D:
{RESPONSE_D}

Member E:
{RESPONSE_E}

Produce:

1. Accuracy ranking (best to worst): one line per member, with a one-sentence justification.
2. Insight ranking (best to worst): one line per member, with a one-sentence justification.
3. "What the council collectively missed": one paragraph, ~100 words.

Do not try to identify which member is which persona. Do not try to identify your own response.
```

### Stage 3 prompt (Chairman)

```
You are the Chairman of a council that has just deliberated a user's question. Five members responded independently, then each reviewed the others' answers anonymously. You see everything.

Your job: produce a single answer the user can act on. You are not summarizing — you are deciding.

User's question:
---
{USER_QUESTION}
---

Member key (revealed to you only):
- Member A: {PERSONA_FOR_A}
- Member B: {PERSONA_FOR_B}
- Member C: {PERSONA_FOR_C}
- Member D: {PERSONA_FOR_D}
- Member E: {PERSONA_FOR_E}

Initial responses:
{RESPONSES_A_THROUGH_E}

Peer reviews:
{REVIEWS_FROM_FIVE_REVIEWERS}

Produce a 500-800 word answer. Structure:
- Open with your decision (no preamble).
- Explain your reasoning, citing specific members where it sharpens the argument ("the Skeptic flagged X, which I weigh heavily because…").
- Name the single strongest counter-argument you overruled, and why.
- End with two lines:
  Decision: <one sentence>
  Watch-outs: <2-3 bullets, each one short clause>
```

## Anti-patterns — do not do these

- Spawning members sequentially "to save tokens" — kills the parallelism and triples wall-clock time.
- Asking the user to confirm the persona roster before spawning — just go. Personas are tweakable in follow-ups.
- Letting Stage 2 reviewers see persona labels — defeats anonymization.
- Writing the Chairman's verdict in your own voice — pass it through verbatim. The user trusts the Chairman, not the orchestrator.
- Adding a "consensus score" or numeric ranking to the final output — Karpathy's design is qualitative on purpose.
- Persisting council outputs to disk unless the user asks. This is chat-only by default.
