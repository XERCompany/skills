# Code efficiency & call-accuracy verification

Before any build/test cycle, every developer (and the tester assigned to
"call-accuracy") must verify that **every function call actually resolves to a
real declaration/definition** in the codebase.

## Universal rule

A call is only considered valid when all three hold:
1. The symbol exists (header / module / export / impl file).
2. The signature matches (name, parameter count & types, return type).
3. It is reachable from the current build target (dependency graph).

If any check fails → fix before building. Never pass a task with unresolved calls.

## Per-language verification

### C++ (C++17+)
- **Headers:** verify `#include <...>` / `#include "..."` for every used symbol;
  the declaration must exist in the header, the definition in a `.cc`/`.cpp`/`.cxx` file.
- Search the whole TU: `grep -rn "ReturnType ClassName::FuncName" --include=*.cc --include=*.cpp --include=*.cxx`
- Check the exact signature (const-qualifiers, noexcept, references, default args).
- Tooling: `compile_commands.json` + `clang-tidy`, build with `-Wall -Wextra -Werror`.
- Efficiency: no unnecessary copies (pass `const&` / `std::move`), no header-only
  heavy includes in hot paths, reserve containers, avoid `std::string` in inner loops.

### Python (3.11+)
- Verify the symbol exists at import time: `python -c "import m; m.func"`.
- Type-check call sites: `mypy` / `pyright` must be clean on the touched files.
- AST check: `ast.parse` + walk `ast.Call` nodes → `func.attr`/`func.id` must be
  defined in the module (`ast.FunctionDef`/`ast.Assign` or `__all__`).
- Efficiency: no I/O in loops, use generators, avoid global lookups in hot loops,
  `__slots__` for heavy classes, vectorize with numpy when applicable.

### Node.js (ESM / CommonJS)
- Verify the export exists: `import * as m from './x.js'; console.log(typeof m.func)`.
- Run with `node --check` on files and `tsc --noEmit` if JSDoc/TS types present.
- Package entry: confirm `exports`/`main` in `package.json` resolves the module.
- Efficiency: no sync fs/`execSync` in request paths, stream large files,
  avoid deep synchronous recursion, cache module-level constants.

### Lua (5.4)
- Verify the symbol in the module table: `local m = require("mod"); assert(type(m.func)=="function")`.
- Lint: `luacheck src/` must report 0 errors.
- Check `require` paths match real files (`mod/init.lua` vs `mod.lua`).
- Efficiency: localise globals inside hot functions, avoid table allocation in
  loops, reuse tables via clear+fill instead of recreating.

### Rust (2021+)
- The compiler is the source of truth: `cargo check` + `cargo clippy -- -D warnings`
  must pass — unresolved calls fail compilation by design.
- Verify trait methods exist for the receiver type; check `use` paths and
  feature flags in `Cargo.toml`.
- Efficiency: prefer iterators over index loops, avoid `clone()` unless needed,
  use `&str`/`Cow` over `String` in read-only paths, `#[inline]` only with reason.

### C# (.NET 8+)
- `dotnet build` with `TreatWarningsAsErrors=true` — missing members fail the build.
- Verify partial classes: the member must exist in *any* part of the `partial` type.
- Nullable context enabled; check extension methods are imported via their namespace.
- Efficiency: avoid `async`-void, use `StringBuilder` in loops, `Span<T>`/`Memory<T>`
  for hot paths, avoid LINQ in inner loops, cache `Task` results where safe.

## Efficiency gates (checked by the tester, role: call-accuracy / perf)
| Gate | Threshold |
|---|---|
| Unresolved / mismatched calls | 0 |
| Compiler/linter warnings in touched files | 0 |
| Unit coverage on touched code | ≥ 80 % |
| Build time regression vs baseline | ≤ +10 % |
| p95 latency regression (if benchmarked) | ≤ +5 % |
| Dead code introduced | 0 |

## Report format (per developer)
`task-id | language | calls checked | unresolved | signature mismatches | perf notes`
