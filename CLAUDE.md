# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **TcEx 4.0** — the ThreatConnect Exchange App Framework, a Python **library/SDK** used to
build ThreatConnect Apps (Playbook, Job, Service, and External Apps). It is not a web service; there
is no Docker/DB/frontend stack.

- **Language**: Python 3.11+
- **Models**: Pydantic **v1** (the codebase pins `pydantic<2.0.0`)
- **Packaging / envs**: managed with **uv** (a `uv` workspace; `uv.lock` + `.venv` at the repo root)
- **Type checker**: **ty** (Astral) — pyright is no longer used (config in root `[tool.ty]`)
- **Linter / formatter**: **ruff** (100-char line length)

The workspace root is **always**
`/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0`. The venv is **always**
`/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv`.

## Repository & Branching

This local repo is a **fork**. `origin` points at the fork; `upstream` is the ThreatConnect repo.

- **All work happens directly on the `main` branch** — `main` is the working branch here, not a
  protected trunk. Do **not** create feature branches; commit changes to `main` unless the operator
  has **manually** switched to another branch first.
- Claude Code must **never change branches itself** (enforced by `enforce_no_branch_change.sh`). If a
  branch change is genuinely needed, the human operator performs it; subsequent work then targets
  whatever branch is currently checked out.
- The usual "branch before committing on the default branch" convention does **not** apply to this
  fork — commits to `main` are expected (when the operator makes them — see below).

### Commits are the operator's job — Claude never commits

**Claude Code must NEVER create a git commit.** ALL commits — in the parent repo **and** in every
submodule — are made by the **human operator**. This is enforced by `enforce_no_commit.sh` (a
PreToolUse hook) and a `Bash(git commit:*)` deny rule; both block `git commit` in any form
(`-m`, `-a`, `--amend`, `git -C <submodule> commit`, after `&&`/pipes, …) with no override.

Claude's role stops at **preparing** the change:

- Make the edits, then `git add` the relevant paths (staging is allowed).
- Run `git status` / `git diff --cached` to show exactly what is ready.
- **Report** what is staged and the suggested commit message(s); the operator runs `git commit`.
- The same applies to submodule changes: stage inside the submodule and describe the two-step
  commit + pointer bump, but let the operator perform both commits.

## Git Submodules

Several parts of `tcex/` are **independent git submodules**, each with its own repository and its own
`pyproject.toml`:

| Submodule path | Notes |
|---|---|
| `tcex/app/config` | install.json / app-spec models + transform builder |
| `tcex/app/key_value_store` | KV store (redis / fakeredis) |
| `tcex/app/playbook` | playbook create/read |
| `tcex/pleb` | shared primitives (cached_property, jmespath functions, registry) |
| `tcex/requests_tc` | ThreatConnect session + auth |
| `tcex/util` | general utilities |

**Editing a submodule is a two-step commit:** commit the change **inside the submodule repo first**,
then bump the submodule pointer in the parent repo. Never assume a parent-repo commit captures
submodule edits. A single logical change can therefore span the parent repo and one or more
submodules.

## Generated Code — `tcex/api/tc/v3`

Most of `tcex/api/tc/v3/**` (the V3 API client: `*_model.py`, object files, `*_filter.py`) is
**generated** by the code generator in `tcex/api/tc/v3/_gen/`.

- **Never hand-edit generated files.** Fix the generator in `tcex/api/tc/v3/_gen/` instead, then
  regenerate. Hand-edits are silently lost on the next regeneration.
- **Regenerate with:**
  ```bash
  # requires .env at the repo root with TC_API_PATH + TC_API_ACCESS_ID + TC_API_SECRET_KEY
  set -a; . /Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.env; set +a
  /Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/python \
    /Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/tcex/api/tc/v3/_gen/_gen.py all
  ```
- The chosen `TC_API_PATH` server **determines the schema** the models are generated against. Use a
  server whose schema matches the intended target; a stale/behind server will drop or alter fields.
- After regenerating, run `pre-commit run --all-files` — the generator output is post-formatted by
  ruff/isort, and that combination (generator output + formatting) is the committed state.
  - The raw generator output intentionally differs from the committed state before this step:
    `tcex/util/code_operation.py::format_code()` runs isort with `known_third_party=['tcex']`
    (correct — that formatter is shared with external Apps, where `tcex` *is* a third-party dep), so
    it emits `# third-party` headings for `tcex.*` imports. The standalone `isort` **pre-commit hook**
    (pyproject `[tool.isort]`, empty `known_*` → auto-detect) then re-labels them `# first-party`, and
    `ruff-format` normalizes quotes to single. This two-config split is **by design — do not "fix"
    `code_operation.py`.** Always run `pre-commit run --all-files` after regenerating.
- The generator fetches the **live API schema over HTTP**, so `TC_API_PATH` + `TC_API_ACCESS_ID` +
  `TC_API_SECRET_KEY` must be in the environment (source `.env` first). Without them the server
  resolves to `None` and the run crashes with `MissingSchema: Invalid URL 'None/v3/...'`.
- `tcex/api/tc/v3/_gen/` itself is hand-written source; the `tcex/api/tc/v2` tree is excluded from ty.

## Development Commands

Dependencies are managed with **uv**. The workspace root holds `uv.lock` and `.venv`; the root
`pyproject.toml` declares dependency groups, and each submodule has its own `pyproject.toml`.

```bash
# Sync the venv to the lock file (runtime + dev + test)
uv sync --group dev --group test

# Code quality (always use the venv's absolute binary paths — see Tool Invocation)
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/ruff check .
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/ruff format .
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/ty check
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pre-commit run --all-files

# Tests (pytest runs with -n auto via pytest-xdist)
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pytest
```

**Managing dependencies:**

```bash
# Add a dev-only tool (root [dependency-groups])
uv add --dev <package>

# Add a test-only tool
uv add --group test <package>

# Regenerate the lock file / sync
uv lock
uv sync --group dev --group test
```

- **Dev & test tooling** (ruff, ty, bandit, pyupgrade, pre-commit, pytest, …) lives in the **root**
  `pyproject.toml` under `[dependency-groups]` (`dev`, `test`).
- **Runtime deps** live in `[project.dependencies]`.
- `uv` may be invoked by bare name (it lives on `PATH` and uses multi-word subcommands).

## Tool Invocation — Absolute Paths Only

**Rule:** every tool invocation MUST use the full absolute path of the binary, and paths must be
**hard-coded** — never resolved dynamically. The workspace root is always
`/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0` and the venv is always
`<root>/.venv`. Do **not** resolve them via `git rev-parse`, `pwd`, `realpath`, `readlink`, `$HOME`,
or `source .venv/bin/activate`.

Three `PreToolUse` hooks (in `.claude/scripts/`) enforce this — treat them as hard rules:

- `enforce_no_dynamic_paths.sh` (Bash) — blocks commands containing path-resolving substitutions:
  `$(git …)`, `$(pwd)`, `$(realpath …)`, `$(readlink …)`, `$(cd … )` (and the backtick forms).
- `enforce_pinned_paths.sh` (Bash) — blocks **bare-name** invocations of standard system utilities;
  use the absolute path instead. It checks **every** command segment (split on `| || && ; |&`), so a
  bare name *after* a pipe is blocked too.
- `enforce_us_spelling.sh` (Write/Edit/NotebookEdit) — blocks British (en-GB) spellings in written
  content.

### Python / venv tools (always absolute `.venv/bin/…`)

```bash
# CORRECT
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/python -c "..."
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pytest tests/util
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/ruff check tcex/util/code_operation.py
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/ty check

# WRONG — re-prompts for every variant / blocked by hooks
cd <root> && .venv/bin/pytest
source .venv/bin/activate && python ...
python3 -c "..."
.venv/bin/pytest          # relative
```

Pass **absolute file paths as arguments**; do not `cd` first.

### System utilities — pinned to Homebrew GNU paths

This project standardizes on the **Homebrew GNU** builds of the standard utilities (coreutils, grep,
gnu-sed, findutils, gawk, gnu-tar, diffutils) in preference to the native macOS BSD tools.
`enforce_pinned_paths.sh` rejects bare-name invocations of these utilities and tells you the exact
absolute path to use. The pinned utilities and their paths:

| Tool(s) | Pinned path prefix |
|---|---|
| `cat head tail sort uniq wc cut tr ls cp mv rm mkdir chmod touch ln stat env date basename dirname tee echo printf du` | `/opt/homebrew/opt/coreutils/libexec/gnubin/` |
| `grep` | `/opt/homebrew/opt/grep/libexec/gnubin/` |
| `find xargs` | `/opt/homebrew/opt/findutils/libexec/gnubin/` |
| `sed` | `/opt/homebrew/opt/gnu-sed/libexec/gnubin/` |
| `awk` | `/opt/homebrew/opt/gawk/libexec/gnubin/` |
| `tar` | `/opt/homebrew/opt/gnu-tar/libexec/gnubin/` |
| `diff` | `/opt/homebrew/opt/diffutils/bin/` |
| `gzip gunzip zcat jq wget` | `/opt/homebrew/bin/` |
| `file` | `/usr/bin/` (no GNU build installed — stays native) |

The hook's `PINNED` map and the `settings.local.json` allowlist are the source of truth — keep all
three in sync. Examples:

```bash
# CORRECT — Homebrew GNU absolute paths
/opt/homebrew/opt/grep/libexec/gnubin/grep -r "pattern" tcex/util
/opt/homebrew/opt/findutils/libexec/gnubin/find tcex -name "*.py" -type f \
  | /opt/homebrew/opt/findutils/libexec/gnubin/xargs /opt/homebrew/opt/grep/libexec/gnubin/grep "foo"

# WRONG — bare names; the hook blocks with a corrective message naming the exact path
grep -r "pattern" .
find . -name "*.py"
```

> Note: `git`, `docker`, and `uv` are not pinned (multi-word subcommands have their own rules);
> `curl` and `file` stay native (`/usr/bin/`).

## Code Standards

### Style and Language Conventions
- **Spelling**: strictly American English (US) for all natural-language output, code comments, and
  docs. The `enforce_us_spelling.sh` hook blocks en-GB variants.
- Prefer `-ize` over `-ise`, `-or` over `-our`, `-er` over `-re`, single `l` over `ll`
  (e.g. "initialize", "color", "center", "canceled").

### Python
- **Formatter / linter**: ruff, 100-char line length, config in root `[tool.ruff]`.
- **Type hints**: required; checked with **ty** (config in root `[tool.ty]`). The `tests/` tree and
  `tcex/api/tc/v2` are excluded.
- **Type-checker suppressions**: ty uses `# type: ignore` (blanket, PEP 484) and
  `# ty: ignore[<rule>]` (targeted). Pyright-style codes like `# type: ignore[reportXxx]` do **not**
  work in ty. Prefer a real type fix; use a targeted `# ty: ignore[<rule>]` only when the code is
  correct but ty cannot infer it.
- **Docstrings**: Google style. **Imports**: organized by isort.
- **pydantic v1** patterns throughout (`validator`, `ModelField`, `update_forward_refs`, etc.).

### Scripts CLI Standard — typer + rich, dry-run by default
Every operator-facing standalone script uses **typer** (CLI) + **rich** (output); mutating scripts
are **dry-run by default — pass `--commit` to write** (no `--dry-run`, no `--yes`). `temp_*` helpers
are exempt from the full standard. **All standalone scripts are authored by the
`python-script-specialist` agent** (see Agents).

### Bandit `# nosec` placement
The suppressor must sit on the **exact line** bandit flags, not a parent call. Always include the
specific test id and a justification, e.g. `subprocess.run(cmd)  # nosec B603 — args are static`.

### Shell / Bash
- **Never use `find -exec`** — pipe through `xargs` instead (`-exec` spawns a subprocess per match):
  ```bash
  /opt/homebrew/opt/findutils/libexec/gnubin/find tcex -name "*.pyc" \
    | /opt/homebrew/opt/findutils/libexec/gnubin/xargs /opt/homebrew/opt/coreutils/libexec/gnubin/rm -f
  ```
  For paths with spaces, use `-print0` / `-0`.

## Testing

- pytest runs with `-n auto` (pytest-xdist); `testpaths = ["tests"]`. If `.venv/bin/pytest` is
  missing, sync the test group once: `uv sync --group test`.
- Test layout mirrors the package: `tests/<area>/` (e.g. `tests/util`, `tests/input`, `tests/app`,
  `tests/api`, `tests/requests_tc`, `tests/pleb`).
- Redis-backed code is tested with **fakeredis**; structural comparisons use **deepdiff**.

```bash
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pytest                 # all
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pytest tests/util      # one area
/Users/bsummers/WorkBench/010__DEVELOPMENT/SDK/tcex-packages/tcex-4.0/.venv/bin/pytest -k "test_name"  # by pattern
```

## Agents

This project uses an orchestrator + specialist subagents (in `.claude/agents/`). The default agent is
`tcex-orchestrator` (set in `.claude/settings.local.json`).

| Agent | Use for |
|---|---|
| `tcex-orchestrator` | Analyzes the request, gathers context, writes a plan when required, delegates to specialists, then runs the security gate and reports. Does not write code itself. |
| `python-engineer` | **All** updates to the tcex codebase under `tcex/` (incl. submodules): models, framework logic, the `_gen/` generator (and regeneration). Not scripts, not tests. |
| `python-test-engineer` | **All** pytest test cases under `tests/`. Does not modify source. |
| `python-script-specialist` | **Sole author** of standalone scripts (typer + rich, dry-run/`--commit`). Writes to `.claude/scripts/`. |
| `python-security-auditor` | **Hard security gate** — runs after every code/test/script change; HIGH/critical findings block "done" until fixed. |

## One-Off Scripts (`.claude/scripts/`)

All standalone scripts are authored by `python-script-specialist`. Agent-written helpers live in
`.claude/scripts/`. A genuine one- or two-line `-c` invocation for ad-hoc context-gathering is fine
and does not need delegation. Python scripts must use the venv's absolute `python` path.

| Script type | Prefix | Example |
|---|---|---|
| Reusable | _(none)_ | `audit_field_types.py` |
| Throwaway | `temp_` | `temp_check_counts.py` |

`temp_*` files are gitignored; reusable scripts are committed with the session.
