---
name: seo-it
description: Multi-agent IT project development. A president agent manages a team
  of 3–6 developers (C++, Python, Node.js, Lua, Rust, C#), 4–6 testers, and 2–4
  API doc writers (for open-source GitHub repos). Includes call-accuracy and
  efficiency verification per language, plus PDF/DOCX/TXT export via Python or
  Node.js scripts. Use for "build/develop/test a project", "agent team", "SEO IT".
---

# SEO IT — team-based development skill

## Roles & headcount

| Role | Agents | Responsibilities |
|---|---|---|
| Project President | 1 | Planning, task assignment, deadline control, final review |
| Developer | 3–6 | Code in C++, Python, Node.js, Lua, Rust, C# + call verification |
| Tester | 4–6 | Unit, integration, regression, performance, call-accuracy tests |
| API Doc Writer | 2–4 | OpenAPI/Swagger, README, CHANGELOG — **only if open on GitHub**; also PDF/DOCX/TXT export |

Headcount from `team.json`; defaults: 4 developers, 5 testers, 3 doc writers.

## When to run

User asks to create/evolve a project, mentions "SEO IT", "agent team", asks for
parallel multi-language development, or asks for efficiency/call checks or
PDF/DOCX/TXT export.

## Orchestration rules

1. **Always start with the president** (`task-breakdown`), then launch the rest.
2. **Parallelism:** developers work simultaneously, each on its own module/language.
3. **Efficiency gate (NEW):** before any build, every developer runs the
   call-accuracy check from `references/efficiency.md` for their language
   (headers/`.cc/.cpp/.cxx` for C++, exports for Node.js, imports/AST for Python,
   module tables for Lua, compiler for Rust, build+analyzers for C#).
   Zero unresolved calls, zero warnings → otherwise the task does not leave DEV.
4. **Documentation only when `repo.is_github == true`** and the repo is public;
   otherwise doc writers assist testers.
5. **Export (NEW):** any request for PDF/DOCX/TXT is fulfilled by running
   `scripts/export_*.py` or `scripts/export.js` (see `references/export.md`).
   Never hand-write binary formats.
6. **No direct commits to `main`** — branches `feature/*`, `test/*`, `docs/*`.
7. **Only the president gives the final "done".**
8. If work is scarce, shrink to the minimum team (3 dev / 4 QA / 2 docs).

## Step-by-step process

1. **PLAN** → president → `plan.json` (tasks, owner, language, done criteria).
2. **DEV** → 3–6 × `developer` in parallel; each ends with the efficiency report:
   `task-id | language | calls checked | unresolved | mismatches | perf notes`.
3. **EFFICIENCY GATE** → president verifies all developers returned
   `unresolved = 0`; failures bounce back to DEV.
4. **BUILD** → president checks toolchains (cmake, cargo, npm, luarocks, dotnet, pip/uv)
   and performs a single clean build.
5. **TEST** → 4–6 × `tester` in parallel: unit / integration / regression /
   performance / call-accuracy / security. Max 3 test→fix cycles, then escalate.
6. **DOCS** → GitHub only: 2–4 × `docwriter` → OpenAPI, README, CHANGELOG,
   and, if requested, `out/*.pdf|docx|txt` via export scripts.
7. **EXPORT (on demand)** → docwriter runs `scripts/export_*`, verifies the file
   (size > 0, re-openable), and reports the path.
8. **REVIEW** → president → final report to the user.

## Answer format for the user

`Status | Task | Language | Agent | Calls OK | Tests | Docs | Export`
plus coverage, known risks and open questions.

## Notes

- Reply in the language of the user's last message.
- Subagents return short markdown reports, not full code.
- If not open on GitHub: "API documentation skipped: repository is not open on GitHub."
- If export deps are missing: install with the commands from `references/export.md`.
