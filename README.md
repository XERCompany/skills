 
```markdown
# SEO IT — Multi-Agent Development Skill

A Claude Code skill that organizes a **team of AI agents** to design, build,
test, document and export an IT project across multiple languages.

```
President (1)  ──►  Developers (3–6)  ──►  Build  ──►  Testers (4–6)  ──►  Doc Writers (2–4)
   plans & controls      C++ · Python         gate      unit/integration     API docs (GitHub)
                         Node.js · Lua                  regression/perf      PDF · DOCX · TXT
                         Rust · C#                       call-accuracy
```

---

## Team & headcount

| Role | Agents | Count | Responsibilities |
|---|---|---|---|
| **President** | `president` | **1** | Planning, task assignment, scheduling, efficiency gate, final review & report |
| **Developers** | `developer` | **3–6** | Code in C++, Python, Node.js, Lua, Rust, C# + per-language call verification |
| **Testers** | `tester` | **4–6** | Unit, integration, regression, performance, call-accuracy, security — after build |
| **Doc Writers** | `docwriter` | **2–4** | OpenAPI/README/CHANGELOG for open GitHub repos + PDF/DOCX/TXT export |

All counts live in `team.json` (`min` / `max` / `default`). If work is scarce the
team shrinks to the minimum: 3 developers · 4 testers · 2 doc writers.

---

## Repository layout

```
.claude/
├── skills/
│   └── seo-it/
│       ├── SKILL.md                  ← skill entry point & orchestration rules
│       ├── team.json                 ← team sizes, efficiency gates, export config
│       └── references/
│           ├── workflow.md           ← PLAN → DEV → GATE → BUILD → TEST → DOCS → EXPORT → REVIEW
│           ├── efficiency.md         ← call-accuracy & performance rules per language
│           ├── export.md             ← PDF / DOCX / TXT pipeline
│           └── checklist.md          ← build / test / docs / export checklists
├── agents/
│   ├── president.md                  ← 1 lead agent
│   ├── developer.md                  ← 3–6 coding agents
│   ├── tester.md                     ← 4–6 QA agents
│   └── docwriter.md                  ← 2–4 documentation & export agents
scripts/
├── export_txt.py                     ← Markdown/JSON → TXT  (stdlib only)
├── export_pdf.py                     ← Markdown → PDF       (fpdf2 + DejaVu TTF)
├── export_docx.py                    ← Markdown → DOCX      (python-docx, tables)
└── export.js                         ← Node.js fallback     (pdfkit + docx)
out/                                  ← generated artifacts (git-ignored)
```

---

## Pipeline

| # | Phase | Who | Exit criteria |
|---|---|---|---|
| 1 | **PLAN** | President | `plan.json`: task, language, assignee, done criteria |
| 2 | **DEV** | 3–6 developers (parallel, one module/language each) | Code + efficiency report |
| 3 | **EFFICIENCY GATE** | President | `unresolved = 0`, `signature mismatches = 0`, 0 warnings |
| 4 | **BUILD** | President | One clean build; toolchains: cmake · cargo · npm · luarocks · dotnet · pip/uv |
| 5 | **TEST** | 4–6 testers (parallel, by discipline) | Coverage ≥ 80 %, 0 critical bugs, 0 high/critical vulns · max 3 test→fix cycles |
| 6 | **DOCS** | 2–4 doc writers — **only if the repo is public on GitHub** | `openapi.yaml`, README, CHANGELOG, runnable examples |
| 7 | **EXPORT** | Doc writers (on demand) | `out/*.pdf|docx|txt`, size > 0, re-openable |
| 8 | **REVIEW** | President | Final report to the user |

Rules: no direct commits to `main` (`feature/*`, `test/*`, `docs/*`); only the
president gives the final "done"; if the repo is not open on GitHub the docs
stage is skipped and doc writers assist the testers.

---

## Call accuracy & efficiency (per language)

Before any build, **every call must resolve to a real symbol with a matching
signature** — full details in [`references/efficiency.md`](.claude/skills/seo-it/references/efficiency.md).

| Language | How calls are verified | Efficiency focus |
|---|---|---|
| **C++** | `#include` headers checked; definition must exist in a `.cc`/`.cpp`/`.cxx` file; full signature compared; `compile_commands.json` + `clang-tidy`, `-Wall -Wextra -Werror` | `const&`/`std::move`, no heavy includes in hot paths, `reserve()` |
| **Python** | Import-probe (`python -c "import m; m.func"`), `mypy`/`pyright` clean, AST walk of `ast.Call` targets | Generators, no I/O in loops, `__slots__`, vectorization |
| **Node.js** | Export/require resolution, `node --check`, `tsc --noEmit`, `package.json` `exports`/`main` | No sync I/O in request paths, streams, module-level caching |
| **Lua** | `require`-probe of module fields, `luacheck` = 0 errors, real file paths | Localise globals, reuse tables, no allocation in loops |
| **Rust** | `cargo check` + `cargo clippy -- -D warnings` (compiler is the authority), trait/`use` path checks | Iterator over index loops, avoid needless `clone()`, `&str`/`Cow` |
| **C#** | `dotnet build` with warnings-as-errors, partial-class member check, nullable context | No `async void`, `StringBuilder`/`Span<T>`, no LINQ in inner loops |

**Gates:** unresolved calls `0` · signature mismatches `0` · warnings `0` ·
coverage ≥ 80 % · build-time regression ≤ +10 % · p95 latency regression ≤ +5 % ·
dead code `0`.

---

## Export: PDF · DOCX · TXT

Binary formats are **never written by hand** — always via Python or Node.js
scripts (see [`references/export.md`](.claude/skills/seo-it/references/export.md)):

```bash
# Python (preferred)
python -m pip install fpdf2 python-docx
python scripts/export_txt.py  --input report.md --out out/report.txt
python scripts/export_pdf.py  --input report.md --out out/report.pdf  --title "SEO IT Report"
python scripts/export_docx.py --input report.md --out out/report.docx

# Node.js (fallback / alternative)
npm install pdfkit docx
node scripts/export.js --input report.md --out out/report.pdf
node scripts/export.js --input report.md --out out/report.docx
node scripts/export.js --input report.md --out out/report.txt
```

* **PDF** — `fpdf2` (or `pdfkit`); Cyrillic requires embedded TTF
  (`assets/fonts/DejaVuSans.ttf`).
* **DOCX** — `python-docx` (or `docx`); Markdown tables → native DOCX tables.
* **TXT** — pure stdlib, UTF-8, LF, wrapped at 100 chars.
* Success = exit code `0` + `OK <path> (<size> bytes)`; failure =
  `EXPORT_ERROR: <reason>` + exit code `1`. Every file is re-opened and
  size-verified.

---

## Installation

```bash
# 1. Copy the skill into your project
mkdir -p .claude
# place skills/seo-it/ and agents/ as shown in Repository layout

# 2. Install export dependencies (only if you need PDF/DOCX/TXT)
python -m pip install fpdf2 python-docx     # Python path
npm install pdfkit docx                     # Node path

# 3. Optional: Cyrillic font for PDF
mkdir -p assets/fonts && cp /path/to/DejaVuSans.ttf assets/fonts/
```

---

## Usage

```bash
# inside Claude Code
/skill seo-it

# or just ask naturally
"SEO IT: build a REST API gateway in Rust + Python with tests and a PDF report"
"SEO IT: efficiency check — verify all function calls in the C++ module"
"SEO IT: export the API docs to DOCX"
```

The president computes the exact team size from the `team.json` ranges and
launches agents in parallel via the `Task` tool.

### Expected final report

```
Status: 🟢 | Task | Language | Agent | Calls OK | Tests | Docs | Export
Coverage: 87 % · Critical bugs: 0 · Unresolved calls: 0
Risks: …   Open questions: …
```

---

## Configuration (`team.json` summary)

| Key | Meaning | Default |
|---|---|---|
| `team.developers / testers / docwriters` | `{min, max, default}` headcount | 4 / 5 / 3 |
| `languages` | Supported stack | C++, Python, Node.js, Lua, Rust, C# |
| `efficiency.*` | Gates (calls, coverage, regressions) | see above |
| `export.*` | Formats, output dir, font, verification | pdf/docx/txt → `out/` |
| `docs.enabled_if` | GitHub condition for API docs | `repo.is_github AND repo.is_public` |
| `limits.build_test_cycles_max` | Test→fix iterations before escalation | 3 |

--- 
