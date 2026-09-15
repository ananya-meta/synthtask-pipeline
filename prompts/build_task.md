Build one complete Terminal-Bench task from the provided task contract.

Workspace root: {{WORKSPACE_ROOT}}
Task directory to populate: {{TASK_DIR}}

Contract:

{{TASK_CONTRACT_MD}}

Requirements:

1. Write all task files under `{{TASK_DIR}}` only. Do not modify files outside the
   workspace root.
2. Create a standard single-turn task layout:
   - `README.md`
   - `task.toml`
   - `instruction.md`
   - `environment/Dockerfile`
   - `tests/test.sh`
   - one or more verifier files under `tests/`
   - `solution/solve.sh`
3. The solver-facing `instruction.md` must be concise and must not mention hidden
   tests, verifier internals, exact thresholds, or the reference solution.
4. The verifier must be binary and implementation-independent. It should fail before
   the reference solution and pass after `solution/solve.sh`.
5. `tests/test.sh` must write `/logs/verifier/ctrf.json` and derive
   `/logs/verifier/reward.txt` from that CTRF summary under `python3 -I -S`; do not set
   reward directly from `$?` or `PIPESTATUS`.
6. Prefer pure Python and small checked-in fixtures. Use realistic market-shaped data
   when a public live dataset would make the task flaky.
7. Do not create symlinks, hidden controller metadata, network-dependent tests,
   large files, or generated caches.
8. After writing the task, run the verifier from `{{TASK_DIR}}` if possible and fix
   local failures.

Use this task metadata unless the contract requires something narrower:

```toml
schema_version = "1.1"

[task]
name = "codimango/<task-directory-name>"
description = "<one sentence>"
authors = [{name = "Ananya Jain", email = "ananyajain@meta.com"}]
keywords = ["finance", "trading", "evaluation", "agents"]
language = "python"
format = "terminal_bench_single_turn"
workstream = "swe_public_repo"

[metadata]
author_name = "Ananya Jain"
author_email = "ananyajain@meta.com"
difficulty = "hard"
category = "software-engineering"
category_usecase = "process_data"
category_subdomain = "finance_and_accounting"
reward_type = "binary"
tags = ["finance", "trading", "evaluation", "agents"]

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 4096
storage_mb = 10240
gpus = 0
allow_internet = true
mcp_servers = []

[environment.env]

[solution.env]

[verifier]
timeout_sec = 300.0

[agent]
timeout_sec = 600.0
```

Before finishing, leave a short build note in `{{WORKSPACE_ROOT}}/logs/build_note.md`
with:

- files created
- verifier command run
- whether the reference solution was checked
