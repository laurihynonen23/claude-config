---
name: feedback_questions
description: User prefers Claude to proceed without confirmation on obvious choices rather than asking structured questions
type: feedback
---

Don't use structured choice prompts (AskUserQuestion) when the right path is clear. Just take it and explain briefly.

**Why:** User has interrupted/rejected AskUserQuestion flows mid-session when the decision was low-stakes or obvious.

**How to apply:** Reserve questions for genuine forks where the direction actually changes — e.g. architectural decisions, destructive actions, ambiguous requirements. Don't ask about things like "should I run all tests?" when they just said "run the tests."
