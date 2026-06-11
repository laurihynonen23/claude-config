# Claude and Codex configuration

Personal Claude Code configuration and shared skills, with a Windows bootstrap
script that also installs Graphify for Claude Code and Codex.

## Windows setup

Install Claude Code and Codex first, then open PowerShell:

```powershell
git clone https://github.com/laurihynonen23/claude-config.git
Set-ExecutionPolicy -Scope Process Bypass
.\claude-config\setup-windows.ps1
```

The script:

- copies `CLAUDE.md`, Windows settings, and shared skills to `~/.claude`
- copies the same shared skills to `~/.codex/skills`
- installs or upgrades the official `graphifyy` package with `uv`
- registers Graphify globally for Claude Code and Codex
- enables Codex's `multi_agent` feature when the `codex` command is available

Restart Claude Code and Codex after setup.

## Using Graphify

Build persistent project memory once from a project's root:

```text
Claude Code: /graphify .
Codex:       $graphify .
```

Graphify creates `graphify-out/graph.json`, `GRAPH_REPORT.md`, and an interactive
`graph.html`. Future agent sessions can query that graph instead of rediscovering
the whole repository.

Refresh the graph after substantial project changes:

```text
Claude Code: /graphify . --update
Codex:       $graphify . --update
```

## Designing agent loops

Use the shared loop-design skill to inspect a project, suggest useful recurring
agent workflows, or turn one goal into a bounded loop with memory and
verification:

```text
Claude Code: /design-agent-loops
Codex:       $design-agent-loops
```

Example:

```text
Inspect this project and rank the three highest-value closed agent loops we
could build. Design a narrow pilot for the best one.
```
