# Projects Monorepo — Agent Instructions

This is a monorepo. Each subdirectory is an independent project.

## Harness Convention

Every project participates in the agent workflow via a `harness/` directory. Read `harness/progress.txt` first to understand what previous sessions accomplished.

### Structure

```
<project>/harness/
  init.sh        — Install deps, verify env (idempotent)
  verify.sh      — Run tests, build checks (exit 0 = pass)
  features.json  — Feature inventory with pass/fail tracking
  progress.txt   — Append-only session log
```

### Root Harness Scripts

- `harness/init.sh [project]` — Run a project's init, or all projects if no arg
- `harness/verify.sh [project]` — Run a project's verify, or all projects if no arg

### Agent Prompt Templates

- `harness/prompts/initializer.md` — Bootstrap a new project's harness
- `harness/prompts/coder.md` — Standard coding session ritual

## Rules

- **Never remove features** from `features.json` — only add or update `passes`
- **One feature per session** — pick the next `passes: false` and focus on it
- **Always update `progress.txt`** at session end — this is the handoff to the next session
- **Always run `verify.sh`** before and after making changes

## Commit Messages

Follow conventional commits scoped to the project:

```
feat(project): description
fix(project): description
refactor(project): description
test(project): description
docs(project): description
init(project): harness initialization
```

## Projects

| Project | Type | Stack |
|---------|------|-------|
| val | Stub | TBD |
| Eth-Bot | Trading bot | TypeScript, pnpm |
| crypto/ai-bot-alchemy | ML trading bot | Python, UV |
| crypto/test-x402 | Protocol testing | TS + Python |
| crypto/portfolio | Strategy docs | Markdown |
| Spydar | FPV quadcopter | C, CMake, Pico SDK |
