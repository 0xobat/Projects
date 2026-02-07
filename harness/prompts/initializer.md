# Initializer Agent Prompt

You are bootstrapping the agent harness for the project **{{PROJECT}}**.

## Your Task

Scan the project source code and create the harness convention files so that future Coding Agent sessions can operate autonomously.

## Steps

1. **Explore the project**
   - Read all source files, configs, READMEs, and existing documentation
   - Understand the tech stack, dependencies, and build system
   - Identify existing tests and CI configuration

2. **Create `harness/init.sh`**
   - Install dependencies (e.g., `pnpm install`, `uv sync`, `cmake ..`)
   - Start dev servers if applicable
   - Verify environment health (check required tools are installed)
   - Must be **idempotent** — safe to run multiple times

3. **Create `harness/verify.sh`**
   - Run all tests (unit, integration, e2e)
   - Run type-checking and linting if configured
   - Run build to confirm it succeeds
   - Exit with code 0 on success, non-zero on failure
   - Should produce human-readable output

4. **Create `harness/features.json`**
   - Inventory all features/capabilities of the project
   - Use this schema for each feature:
     ```json
     {
       "id": "F001",
       "category": "functional|infra|test|docs",
       "description": "Short description of the feature",
       "steps": ["Step 1", "Step 2", "..."],
       "passes": false
     }
     ```
   - Set `passes: true` only for features that are fully implemented AND verified
   - Set `passes: false` for planned, partial, or untested features
   - Categories: `functional` (user-facing), `infra` (build/deploy/CI), `test` (test coverage), `docs` (documentation)

5. **Create `harness/progress.txt`**
   - Initialize with a session entry:
     ```
     --- Session {{DATE}} ---
     Worked on: Harness initialization
     Completed: Created harness convention files (init.sh, verify.sh, features.json)
     Blocked: (none)
     Next: Pick first passes:false feature from features.json
     Commit: (pending)
     ```

6. **Create or update `CLAUDE.md`**
   - If the project already has a CLAUDE.md, append a harness reference section
   - If not, create one with project-specific instructions plus harness reference
   - Include: tech stack, how to run, how to test, and pointer to `harness/`

7. **Git commit**
   - Stage all new harness files
   - Commit with message: `init: {{PROJECT}} harness`

## Rules

- Never delete or modify existing source code
- Only create files inside `{{PROJECT}}/harness/` and optionally update `CLAUDE.md`
- features.json must be valid JSON
- All shell scripts must be executable and use `#!/usr/bin/env bash`
