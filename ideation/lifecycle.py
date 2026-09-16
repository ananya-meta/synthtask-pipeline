"""Downstream task-generation lifecycle.

The controller is deliberately boring: it records state, creates isolated workspaces,
and promotes artifacts only through explicit commands. Agent intelligence belongs in
workers; the harness owns the audit trail and the write boundary.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from . import db, generate, seeds

DISCOVERY_DIR = db.REPO_ROOT / "discovery_bundles"
SCAFFOLD_ROOT = db.REPO_ROOT / "runs" / "contracts"

TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}
MAX_CAPTURE_BYTES = 200_000

CONTRACT_FIELDS = (
    "objective",
    "hidden_principle",
    "allowed_inputs",
    "forbidden_leaks",
    "oracle_strategy",
    "mutation_strategy",
    "infra_requirements",
    "difficulty_target",
)

# Free-text fields that have to say something substantive for a builder to act on.
# `infra_requirements` is deliberately excluded: "stdlib Python" is a complete answer.
PROSE_CONTRACT_FIELDS = (
    "objective",
    "hidden_principle",
    "oracle_strategy",
    "mutation_strategy",
    "difficulty_target",
)
MIN_PROSE_WORDS = 4
FILLER_VALUES = {
    "asdf", "asdfasdf", "foo", "bar", "baz", "qux", "test", "testing", "temp", "tmp",
    "tbd", "tba", "todo", "xxx", "yyy", "zzz", "n/a", "na", "none", "null", "nil",
    "placeholder", "lorem", "ipsum", "stuff", "things", "something", "whatever", "-",
}

SCAFFOLD_ALLOWED = {
    "TASK_CONTRACT.json",
    "TASK_CONTRACT.md",
    "PRIOR_ATTEMPTS.md",
    "CONTROLLER_NOTES.md",
    "RUN_PROMPT.md",
    "worker_stdout.log",
    "worker_stderr.log",
    "task",
    "logs",
    "reviews",
    "verification",
}

TRIAGE_ROUTE = {
    "accepted": "done",
    "pending": "poll",
    "published": "poll",
    "draft": "poll",
    "unknown": "poll",
    "infra": "fix_infra",
    "infra_error": "fix_infra",
    "bad_grading_weak": "strengthen_oracle",
    "grading_wrong": "fix_verifier_contract",
    "too_easy": "reduce_leakage_or_add_hidden_state",
    "too_hard": "simplify_or_retarget",
    "leak": "separate_visible_task_from_hidden_scoring",
    "timeout": "reduce_runtime_or_budget",
    "rejected": "triage_feedback",
    "failed_unclassified": "manual_triage",
}

# Codimango has not reached a verdict yet. These must stay visible to the controller:
# a submission row is written as soon as the task is published, so without a re-poll
# stage the task would silently drop out of next_actions forever.
POLLABLE_SUBMISSION_STATUSES = ("pending", "published", "draft", "unknown")
SETTLED_OK_SUBMISSION_STATUSES = ("accepted", "passed")

# A contract in one of these states already owns the idea; drafting a second one just
# fans out duplicate versions. Same idea for scaffolds: anything outside the
# restartable set is still live, so a new revision would race it.
CONTRACT_LIVE_STATES = ("draft", "ready")
SCAFFOLD_RESTARTABLE_STATES = (
    "build_failed",
    "needs_revision",
    "rejected",
    "submitted",
    "accepted",
)

# Stated as an exclusion list on purpose. `scaffold_runs.state` records the last event on
# the row, and seven call sites can write fifteen different values — an allowlist of
# "already built" states silently omits new ones and re-invokes the builder on work that is
# finished. Only these three mean the workspace has no build behind it.
UNBUILT_STATES = ("started", "running", "build_failed")


class LifecycleError(RuntimeError):
    pass


def _marks(values: tuple[str, ...]) -> str:
    return ", ".join("?" for _ in values)


def _now_ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def _read_text_limited(path: Path) -> str:
    data = path.read_bytes()[:MAX_CAPTURE_BYTES]
    return data.decode("utf-8", errors="replace")


def _file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _bundle_key(source: str, path: Path, payload: dict) -> str:
    raw = f"{source}\n{path}\n{_json_dumps(payload)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _load_jsonish(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    text = value.strip()
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def capture_bundle(path: Path) -> dict:
    """Capture a discovery bundle without assuming a specific upstream format."""
    path = path.expanduser().resolve()
    if not path.exists():
        raise LifecycleError(f"discovery bundle path does not exist: {path}")

    if path.is_file():
        entry = {
            "path": path.name,
            "size": path.stat().st_size,
            "sha256": _file_digest(path),
        }
        if path.suffix.lower() in TEXT_SUFFIXES:
            entry["content"] = _read_text_limited(path)
        return {"kind": "file", "files": [entry]}

    files = []
    for child in sorted(p for p in path.iterdir() if p.is_file()):
        entry = {
            "path": child.name,
            "size": child.stat().st_size,
            "sha256": _file_digest(child),
        }
        if child.suffix.lower() in TEXT_SUFFIXES:
            entry["content"] = _read_text_limited(child)
        files.append(entry)
    if not files:
        raise LifecycleError(f"discovery bundle directory has no files: {path}")
    return {"kind": "directory", "files": files}


def ingest_discovery_bundle(
    conn,
    path: Path,
    *,
    seed_ref: str | None = None,
    source: str = "graph-discovery",
    source_url: str = "",
    title: str = "",
    bundle_key: str = "",
) -> int:
    seed_id = None
    if seed_ref:
        seed = db.get_seed(conn, seed_ref)
        if seed is None:
            raise LifecycleError(f"no seed matching {seed_ref!r}")
        seed_id = seed["id"]

    payload = capture_bundle(path)
    key = bundle_key or _bundle_key(source, path.expanduser().resolve(), payload)
    return db.add_discovery_bundle(
        conn,
        seed_id=seed_id,
        bundle_key=key,
        title=title or path.name,
        source=source,
        source_url=source_url,
        path=str(path.expanduser().resolve()),
        payload_json=_json_dumps(payload),
    )


def _field_value(overrides: dict[str, str], field: str, default: str = "") -> str:
    value = overrides.get(field)
    if value is None:
        return default
    return value.strip()


def create_contract(
    conn,
    idea_id: int,
    *,
    discovery_bundle_id: int | None = None,
    force: bool = False,
    **overrides: str,
) -> int:
    idea = db.get_idea(conn, idea_id)
    if idea is None:
        raise LifecycleError(f"no idea #{idea_id}")

    verdict = db.verdict_for(conn, idea_id)
    if not force and (verdict is None or verdict["verdict"] != "accept"):
        raise LifecycleError(
            f"idea #{idea_id} is not accepted; pass --force to draft a contract anyway"
        )

    if not force:
        live = conn.execute(
            "SELECT id, status FROM task_contracts WHERE idea_id = ?"
            f" AND status IN ({_marks(CONTRACT_LIVE_STATES)})"
            " ORDER BY version DESC LIMIT 1",
            (idea_id, *CONTRACT_LIVE_STATES),
        ).fetchone()
        if live is not None:
            raise LifecycleError(
                f"idea #{idea_id} already has {live['status']} contract #{live['id']};"
                " shelve it or pass --force to draft another version"
            )

    raw = json.loads(idea["raw_json"] or "{}")
    default_objective = idea["statement"]
    default_difficulty = idea["difficulty_claim"] or raw.get("difficulty", "")
    contract = {
        "idea_id": idea_id,
        "idea_title": idea["title"],
        "source": {
            "seed_id": idea["seed_id"],
            "run_id": idea["run_id"],
            "discovery_bundle_id": discovery_bundle_id,
        },
        "fields": {
            "objective": _field_value(overrides, "objective", default_objective),
            "hidden_principle": _field_value(overrides, "hidden_principle"),
            "allowed_inputs": _load_jsonish(overrides.get("allowed_inputs"), []),
            "forbidden_leaks": _load_jsonish(overrides.get("forbidden_leaks"), []),
            "oracle_strategy": _field_value(overrides, "oracle_strategy"),
            "mutation_strategy": _field_value(overrides, "mutation_strategy"),
            "infra_requirements": _field_value(overrides, "infra_requirements"),
            "difficulty_target": _field_value(overrides, "difficulty_target", default_difficulty),
        },
        "review": {
            "assumption_broken": idea["assumption_broken"],
            "dataset_ref": idea["dataset_ref"],
        },
    }
    fields = contract["fields"]
    values = {
        "idea_id": idea_id,
        "discovery_bundle_id": discovery_bundle_id,
        "objective": str(fields["objective"]),
        "hidden_principle": str(fields["hidden_principle"]),
        "allowed_inputs": _json_dumps(fields["allowed_inputs"]),
        "forbidden_leaks": _json_dumps(fields["forbidden_leaks"]),
        "oracle_strategy": str(fields["oracle_strategy"]),
        "mutation_strategy": str(fields["mutation_strategy"]),
        "infra_requirements": str(fields["infra_requirements"]),
        "difficulty_target": str(fields["difficulty_target"]),
        "contract_json": _json_dumps(contract),
    }
    return db.add_task_contract(conn, **values)


def contract_dict(row) -> dict:
    obj = json.loads(row["contract_json"])
    obj["id"] = row["id"]
    obj["version"] = row["version"]
    obj["status"] = row["status"]
    obj["created_at"] = row["created_at"]
    obj["updated_at"] = row["updated_at"]
    return obj


def _is_filler(value: str) -> bool:
    stripped = value.strip().strip(".").lower()
    return stripped in FILLER_VALUES or all(
        word in FILLER_VALUES for word in stripped.split()
    )


def validate_contract(row) -> list[str]:
    """Reasons this contract is not ready, as machine-readable `field:reason` strings.

    A heuristic floor, not a judgement of quality: it cannot tell a weak hidden principle
    from a strong one, only a real one from a placeholder. The contract is the only thing
    the builder reads, so `hidden_principle="asdf"` reaching `ready` is worth catching even
    if `hidden_principle="hide the oracle"` still gets through.
    """
    missing = []
    for field in CONTRACT_FIELDS:
        value = (row[field] or "").strip()
        if not value or value.startswith("TODO"):
            missing.append(field)
            continue
        if _is_filler(value):
            missing.append(f"{field}:placeholder")
            continue
        if field in PROSE_CONTRACT_FIELDS and len(value.split()) < MIN_PROSE_WORDS:
            missing.append(f"{field}:too_short")

    parsed_lists: dict[str, list] = {}
    for field in ("allowed_inputs", "forbidden_leaks"):
        try:
            parsed = json.loads(row[field])
        except json.JSONDecodeError:
            missing.append(f"{field}:invalid_json")
            continue
        if not parsed:
            missing.append(field)
            continue
        entries = [str(item).strip() for item in parsed if str(item).strip()]
        if not entries or all(_is_filler(entry) for entry in entries):
            missing.append(f"{field}:placeholder")
            continue
        parsed_lists[field] = entries

    allowed = parsed_lists.get("allowed_inputs")
    forbidden = parsed_lists.get("forbidden_leaks")
    if allowed and forbidden and {a.lower() for a in allowed} == {f.lower() for f in forbidden}:
        # If everything the agent may read is also a forbidden leak, the contract has not
        # actually decided what is hidden.
        missing.append("forbidden_leaks:same_as_allowed_inputs")

    return missing


def mark_contract_ready(conn, contract_id: int) -> list[str]:
    row = db.get_task_contract(conn, contract_id)
    if row is None:
        raise LifecycleError(f"no contract #{contract_id}")
    missing = validate_contract(row)
    if missing:
        return missing
    db.update_task_contract_status(conn, contract_id, "ready")
    return []


def _contract_markdown(contract: dict) -> str:
    fields = contract["fields"]
    return "\n".join(
        [
            f"# Task Contract: {contract['idea_title']}",
            "",
            f"- Idea ID: {contract['idea_id']}",
            f"- Contract version: {contract['version']}",
            f"- Status: {contract['status']}",
            "",
            "## Objective",
            str(fields["objective"]),
            "",
            "## Hidden grading principle",
            str(fields["hidden_principle"]),
            "",
            "## Allowed inputs",
            _json_dumps(fields["allowed_inputs"]),
            "",
            "## Forbidden leaks",
            _json_dumps(fields["forbidden_leaks"]),
            "",
            "## Oracle strategy",
            str(fields["oracle_strategy"]),
            "",
            "## Mutation strategy",
            str(fields["mutation_strategy"]),
            "",
            "## Infra requirements",
            str(fields["infra_requirements"]),
            "",
            "## Difficulty target",
            str(fields["difficulty_target"]),
            "",
        ]
    )


def start_scaffold(
    conn,
    contract_id: int,
    *,
    builder: str = "manual",
    model: str = "",
    revision: int | None = None,
    allow_draft: bool = False,
) -> tuple[int, Path]:
    row = db.get_task_contract(conn, contract_id)
    if row is None:
        raise LifecycleError(f"no contract #{contract_id}")
    if row["status"] != "ready" and not allow_draft:
        raise LifecycleError(
            f"contract #{contract_id} is {row['status']!r}; mark it ready before scaffolding"
        )
    if row["status"] not in {"ready", "draft"}:
        raise LifecycleError(f"contract #{contract_id} has terminal status {row['status']!r}")

    if revision is None:
        live = conn.execute(
            "SELECT id, state FROM scaffold_runs WHERE contract_id = ?"
            f" AND state NOT IN ({_marks(SCAFFOLD_RESTARTABLE_STATES)})"
            " ORDER BY revision DESC LIMIT 1",
            (contract_id, *SCAFFOLD_RESTARTABLE_STATES),
        ).fetchone()
        if live is not None:
            raise LifecycleError(
                f"contract #{contract_id} already has live scaffold #{live['id']}"
                f" in state {live['state']!r}; pass --revision to start another anyway"
            )
        prior = conn.execute(
            "SELECT MAX(revision) AS r FROM scaffold_runs WHERE contract_id = ?",
            (contract_id,),
        ).fetchone()
        revision = int(prior["r"] or 0) + 1

    root = SCAFFOLD_ROOT / f"{contract_id:04d}" / builder / f"r{revision:02d}-{_now_ts()}"
    for subdir in ("task", "logs", "reviews", "verification"):
        (root / subdir).mkdir(parents=True, exist_ok=True)

    contract = contract_dict(row)
    (root / "TASK_CONTRACT.json").write_text(_json_dumps(contract) + "\n", encoding="utf-8")
    (root / "TASK_CONTRACT.md").write_text(_contract_markdown(contract), encoding="utf-8")
    (root / "PRIOR_ATTEMPTS.md").write_text(
        prior_attempts_markdown(prior_attempts(conn, contract_id, before_revision=revision)),
        encoding="utf-8",
    )
    (root / "CONTROLLER_NOTES.md").write_text(
        "# Controller Notes\n\n"
        "Build inside `task/`. Do not read sibling workspaces or copy files into canonical "
        "locations outside this scaffold root. The controller promotes artifacts explicitly.\n",
        encoding="utf-8",
    )
    assert_scaffold_isolated(root)

    scaffold_id = db.add_scaffold_run(
        conn,
        contract_id=contract_id,
        builder=builder,
        model=model,
        revision=revision,
        workspace_root=str(root),
    )
    db.set_outcome(conn, row["idea_id"], scaffolded=1)
    return scaffold_id, root


def assert_scaffold_isolated(root: Path) -> None:
    stray = [p.name for p in root.iterdir() if p.name not in SCAFFOLD_ALLOWED]
    if stray:
        raise LifecycleError(f"scaffold isolation breach in {root}: unexpected entries {stray}")


def promote_scaffold(conn, scaffold_run_id: int, canonical_root: Path) -> None:
    scaffold = db.get_scaffold_run(conn, scaffold_run_id)
    if scaffold is None:
        raise LifecycleError(f"no scaffold run #{scaffold_run_id}")
    workspace = Path(scaffold["workspace_root"])
    task_dir = workspace / "task"
    if not task_dir.exists():
        raise LifecycleError(f"missing task directory in {workspace}")

    canonical_root = canonical_root.expanduser().resolve()
    if canonical_root.exists() and any(canonical_root.iterdir()):
        raise LifecycleError(f"canonical root is not empty: {canonical_root}")
    canonical_root.mkdir(parents=True, exist_ok=True)
    for child in task_dir.iterdir():
        dest = canonical_root / child.name
        if child.is_dir():
            shutil.copytree(child, dest)
        else:
            shutil.copy2(child, dest)
    db.update_scaffold_run(
        conn,
        scaffold_run_id,
        canonical_root=str(canonical_root),
        state="promoted",
        finished_at=time.time(),
        exit_code=0,
    )


def prior_attempts(conn, contract_id: int, before_revision: int | None = None) -> list[dict]:
    """Per-revision history for a contract: what was tried and how it came back.

    This is the input a revision needs and never had. Without it every revision of a
    contract is built from byte-identical inputs, so a task rejected as `too_easy` twice
    gets rebuilt a third time with no encoding of why.
    """
    query = "SELECT * FROM scaffold_runs WHERE contract_id = ?"
    args: list[Any] = [contract_id]
    if before_revision is not None:
        query += " AND revision < ?"
        args.append(before_revision)
    query += " ORDER BY revision, id"

    attempts = []
    for scaffold in conn.execute(query, tuple(args)).fetchall():
        verifications = conn.execute(
            "SELECT status, command FROM verification_runs"
            " WHERE scaffold_run_id = ? ORDER BY id",
            (scaffold["id"],),
        ).fetchall()
        reviews = conn.execute(
            "SELECT reviewer, kind, verdict, note FROM review_records"
            " WHERE scaffold_run_id = ? ORDER BY id",
            (scaffold["id"],),
        ).fetchall()
        submissions = conn.execute(
            "SELECT id, status, pass_rate FROM submissions"
            " WHERE scaffold_run_id = ? ORDER BY id",
            (scaffold["id"],),
        ).fetchall()

        submission_entries = []
        for row in submissions:
            notes = [
                {
                    "label": event["label"],
                    "detail": event["detail"],
                    "payload": _load_jsonish(event["payload_json"], {}),
                }
                for event in db.learning_events_for(conn, "submission", row["id"])
            ]
            submission_entries.append(
                {
                    "submission_id": row["id"],
                    "status": row["status"],
                    "route": triage_route(row["status"]),
                    "pass_rate": row["pass_rate"],
                    "learnings": notes,
                }
            )

        attempts.append(
            {
                "revision": scaffold["revision"],
                "scaffold_run_id": scaffold["id"],
                "builder": scaffold["builder"],
                "model": scaffold["model"],
                "state": scaffold["state"],
                "verifications": [
                    {"status": v["status"], "command": v["command"]} for v in verifications
                ],
                "reviews": [
                    {
                        "reviewer": r["reviewer"],
                        "kind": r["kind"],
                        "verdict": r["verdict"],
                        "note": r["note"],
                    }
                    for r in reviews
                ],
                "submissions": submission_entries,
                "learnings": [
                    {"label": e["label"], "detail": e["detail"]}
                    for e in db.learning_events_for(conn, "scaffold", scaffold["id"])
                ],
            }
        )
    return attempts


def prior_attempts_markdown(attempts: list[dict]) -> str:
    if not attempts:
        return "No prior attempts — this is the first revision of this contract."

    lines = [
        f"{len(attempts)} prior attempt(s) at this contract. Each was rejected or is "
        "still unresolved; do not reproduce the same outcome.",
        "",
    ]
    for attempt in attempts:
        lines.append(f"## Revision {attempt['revision']} ({attempt['builder']})")
        lines.append(f"- Final state: `{attempt['state']}`")

        failures = [v for v in attempt["verifications"] if v["status"] != "pass"]
        if failures:
            lines.append(f"- Local verification failed {len(failures)} time(s)")
        for review in attempt["reviews"]:
            note = f" — {review['note']}" if review["note"] else ""
            lines.append(f"- Review ({review['reviewer']}): **{review['verdict']}**{note}")
        for submission in attempt["submissions"]:
            rate = (
                f", pass rate {submission['pass_rate']}"
                if submission["pass_rate"] is not None
                else ""
            )
            lines.append(
                f"- Codimango returned **{submission['status']}**{rate}"
                f" → route `{submission['route']}`"
            )
            for note in submission["learnings"]:
                detail = (note["detail"] or "").strip()
                if detail:
                    lines.append(f"    - {note['label']}: {detail}")
        for note in attempt["learnings"]:
            lines.append(f"- {note['label']}: {note['detail']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def revision_guidance() -> str:
    """Human-authored guidance on how to respond to a triage route, if it exists.

    Optional by design: `prompts/` is human-authored, so the harness threads this file in
    when it is written and stays silent when it is not.
    """
    path = db.REPO_ROOT / "prompts" / "revision_guidance.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return "" if text.strip().startswith("<!-- TODO") else text


def _render_scaffold_prompt(template: str, root: Path) -> str:
    contract_json = (root / "TASK_CONTRACT.json").read_text(encoding="utf-8")
    contract_md = (root / "TASK_CONTRACT.md").read_text(encoding="utf-8")
    attempts_path = root / "PRIOR_ATTEMPTS.md"
    attempts_md = (
        attempts_path.read_text(encoding="utf-8") if attempts_path.exists() else ""
    )
    return (
        template.replace("{{TASK_CONTRACT_JSON}}", contract_json)
        .replace("{{TASK_CONTRACT_MD}}", contract_md)
        .replace("{{PRIOR_ATTEMPTS}}", attempts_md)
        .replace("{{REVISION_GUIDANCE}}", revision_guidance())
        .replace("{{WORKSPACE_ROOT}}", str(root))
        .replace("{{TASK_DIR}}", str(root / "task"))
    )


def _build_scaffold_cmd(builder: str, root: Path, prompt: str, model: str | None) -> list[str]:
    if builder == "codex":
        cmd = [
            "codex",
            "exec",
            "--cd",
            str(root),
            "--sandbox",
            "workspace-write",
            "--skip-git-repo-check",
        ]
        if model:
            cmd += ["-m", model]
        cmd += ["--", prompt]
        return cmd

    if builder == "tbh":
        prompt_file = root / "RUN_PROMPT.md"
        cmd = [
            "muse",
            "exec",
            "--workspace",
            str(root),
            "--prompt-file",
            str(prompt_file),
        ]
        if model:
            cmd += ["--model", model]
        return cmd

    raise LifecycleError(f"unknown scaffold builder {builder!r} (expected codex or tbh)")


def run_scaffold_worker(
    conn,
    scaffold_run_id: int,
    prompt_file: Path,
    *,
    timeout: int = 3600,
) -> int:
    scaffold = db.get_scaffold_run(conn, scaffold_run_id)
    if scaffold is None:
        raise LifecycleError(f"no scaffold run #{scaffold_run_id}")
    builder = scaffold["builder"]
    if builder not in {"codex", "tbh"}:
        raise LifecycleError(f"scaffold run #{scaffold_run_id} uses non-agent builder {builder!r}")

    prompt_path = prompt_file.expanduser().resolve()
    if not prompt_path.exists():
        raise LifecycleError(f"prompt file does not exist: {prompt_path}")
    template = prompt_path.read_text(encoding="utf-8")
    if scaffold["revision"] > 1 and "{{PRIOR_ATTEMPTS}}" not in template:
        # Rebuilding from the same inputs that already failed is the failure mode this
        # history exists to prevent, so refuse rather than silently repeat it.
        raise LifecycleError(
            f"scaffold run #{scaffold_run_id} is revision {scaffold['revision']}, but"
            f" {prompt_path} has no {{{{PRIOR_ATTEMPTS}}}} token — the builder would repeat"
            " the previous attempt blind. Add the token to the prompt (the rendered history"
            " is also written to PRIOR_ATTEMPTS.md in the workspace)."
        )
    root = Path(scaffold["workspace_root"])
    prompt = _render_scaffold_prompt(template, root)
    (root / "RUN_PROMPT.md").write_text(prompt, encoding="utf-8")
    assert_scaffold_isolated(root)

    cmd = _build_scaffold_cmd(builder, root, prompt, scaffold["model"])
    db.update_scaffold_run(conn, scaffold_run_id, state="running")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=root)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = -1, "", f"timed out after {timeout}s"

    (root / "worker_stdout.log").write_text(out, encoding="utf-8")
    (root / "worker_stderr.log").write_text(err, encoding="utf-8")
    assert_scaffold_isolated(root)
    db.update_scaffold_run(
        conn,
        scaffold_run_id,
        state="built" if rc == 0 else "build_failed",
        finished_at=time.time(),
        exit_code=rc,
        stderr_tail=err[-2000:],
    )
    return rc


def run_verification(
    conn,
    scaffold_run_id: int,
    command: list[str],
    *,
    verifier: str = "local",
    cwd_choice: str = "workspace",
    timeout: int = 1800,
) -> int:
    if not command:
        raise LifecycleError("verification command is empty")
    scaffold = db.get_scaffold_run(conn, scaffold_run_id)
    if scaffold is None:
        raise LifecycleError(f"no scaffold run #{scaffold_run_id}")

    if cwd_choice == "canonical":
        if not scaffold["canonical_root"]:
            raise LifecycleError("scaffold has no canonical root")
        cwd = Path(scaffold["canonical_root"])
    elif cwd_choice == "task":
        cwd = Path(scaffold["workspace_root"]) / "task"
    elif cwd_choice == "workspace":
        cwd = Path(scaffold["workspace_root"])
    else:
        raise LifecycleError("cwd must be workspace, task, or canonical")

    started = time.time()
    try:
        proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        status = "pass" if proc.returncode == 0 else "fail"
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        status = "timeout"
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    finished = time.time()

    verify_id = db.add_verification_run(
        conn,
        scaffold_run_id=scaffold_run_id,
        verifier=verifier,
        command=shlex.join(command),
        status=status,
        stdout_tail=stdout[-4000:],
        stderr_tail=stderr[-4000:],
        started_at=started,
        finished_at=finished,
    )
    db.update_scaffold_run(
        conn,
        scaffold_run_id,
        state="verified" if status == "pass" else "verification_failed",
    )
    return verify_id


def record_review(
    conn,
    scaffold_run_id: int,
    *,
    reviewer: str,
    kind: str,
    verdict: str,
    issues: list[dict] | None = None,
    note: str = "",
) -> int:
    if db.get_scaffold_run(conn, scaffold_run_id) is None:
        raise LifecycleError(f"no scaffold run #{scaffold_run_id}")
    review_id = db.add_review_record(
        conn,
        scaffold_run_id=scaffold_run_id,
        reviewer=reviewer,
        kind=kind,
        verdict=verdict,
        issues_json=_json_dumps(issues or []),
        note=note,
    )
    next_state = {
        "approve": "reviewed",
        "revise": "needs_revision",
        "reject": "rejected",
    }.get(verdict, "reviewed")
    db.update_scaffold_run(conn, scaffold_run_id, state=next_state)
    return review_id


def record_submission(
    conn,
    scaffold_run_id: int,
    *,
    platform: str,
    status: str,
    external_id: str = "",
    pass_rate: float | None = None,
    revisions: int | None = None,
    result: dict | None = None,
) -> int:
    scaffold = db.get_scaffold_run(conn, scaffold_run_id)
    if scaffold is None:
        raise LifecycleError(f"no scaffold run #{scaffold_run_id}")
    submission_id = db.add_submission(
        conn,
        scaffold_run_id=scaffold_run_id,
        platform=platform,
        external_id=external_id,
        status=status,
        pass_rate=pass_rate,
        revisions=revisions,
        result_json=_json_dumps(result or {}),
    )
    row = conn.execute(
        "SELECT c.idea_id FROM scaffold_runs s"
        " JOIN task_contracts c ON c.id = s.contract_id"
        " WHERE s.id = ?",
        (scaffold_run_id,),
    ).fetchone()
    if row is not None:
        fields: dict[str, Any] = {"submitted_at": time.time()}
        if platform == "smoldata" and external_id:
            fields["smoldata_task_id"] = external_id
        if status == "accepted":
            fields["accepted"] = 1
        elif is_failed_status(status):
            fields["accepted"] = 0
        if pass_rate is not None:
            fields["pass_rate"] = pass_rate
        if revisions is not None:
            fields["revisions"] = revisions
        db.set_outcome(conn, row["idea_id"], **fields)
    db.update_scaffold_run(
        conn,
        scaffold_run_id,
        state="accepted" if status == "accepted" else "submitted",
    )
    if is_failed_status(status):
        _record_failure_learning(conn, submission_id, status, result or {})
    return submission_id


def failure_detail_text(result: dict) -> str:
    """Pull the reviewer prose out of a recorded submission payload.

    Codimango nests the useful sentence several ways depending on which command produced
    the payload, so this walks the known shapes rather than assuming one.
    """
    texts: list[str] = []
    for blob in (result or {}).values():
        if not isinstance(blob, dict):
            continue
        task = blob.get("task") if isinstance(blob.get("task"), dict) else blob
        details = task.get("validationDetails") if isinstance(task, dict) else None
        if isinstance(details, list):
            for item in details:
                if not isinstance(item, dict):
                    continue
                if str(item.get("status", "")).lower() in {"failed", "fail"}:
                    label = str(item.get("label", "")).strip()
                    detail = str(item.get("detail", "")).strip()
                    texts.append(f"{label}: {detail}" if label else detail)
        for key in ("authorFeedback", "feedback", "summary"):
            value = task.get(key) if isinstance(task, dict) else None
            if isinstance(value, str) and value.strip():
                texts.append(value.strip())
    return "\n".join(dict.fromkeys(t for t in texts if t))


def _record_failure_learning(conn, submission_id: int, status: str, result: dict) -> int:
    """Capture the machine-visible half of a failure automatically.

    Without this the triage route is a label nobody records, and the next revision is built
    from the same inputs as the last one. Human notes still go through `learn add`; this
    only guarantees the route and the reviewer prose are never lost.
    """
    route = triage_route(status)
    detail = failure_detail_text(result)
    return record_learning(
        conn,
        scope_type="submission",
        scope_id=submission_id,
        label="smoldata-failure",
        detail=detail or f"Codimango returned {status!r} with no detail text.",
        payload={"status": status, "route": route},
    )


def record_learning(
    conn,
    *,
    scope_type: str,
    scope_id: int,
    label: str,
    detail: str,
    payload: dict | None = None,
) -> int:
    return db.add_learning_event(
        conn,
        scope_type=scope_type,
        scope_id=scope_id,
        label=label,
        detail=detail,
        payload_json=_json_dumps(payload or {}),
    )


def triage_route(status: str) -> str:
    normalized = status.lower().strip()
    if normalized in TRIAGE_ROUTE:
        return TRIAGE_ROUTE[normalized]
    # Unclassified failures carry the raw code as `failed_unclassified:<code>`.
    return TRIAGE_ROUTE.get(normalized.split(":", 1)[0], "manual_triage")


def is_failed_status(status: str) -> bool:
    """Anything that has settled but is not a pass. Kept as the complement of the two
    known-good sets so a new Codimango status is treated as a failure, not as success."""
    normalized = status.lower().strip()
    if not normalized:
        return False
    return (
        normalized not in SETTLED_OK_SUBMISSION_STATUSES
        and normalized not in POLLABLE_SUBMISSION_STATUSES
    )


def pipeline_summary(conn) -> dict:
    q = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    latest_submissions = [
        dict(r)
        for r in conn.execute(
            "SELECT s.id, s.platform, s.external_id, s.status, s.pass_rate,"
            "       s.revisions, sr.contract_id"
            " FROM submissions s"
            " JOIN scaffold_runs sr ON sr.id = s.scaffold_run_id"
            " ORDER BY s.updated_at DESC, s.id DESC LIMIT 8"
        ).fetchall()
    ]
    for item in latest_submissions:
        item["route"] = triage_route(item["status"])
    return {
        "discovery_bundles": q("SELECT COUNT(*) FROM discovery_bundles"),
        "contracts": q("SELECT COUNT(*) FROM task_contracts"),
        "ready_contracts": q("SELECT COUNT(*) FROM task_contracts WHERE status = 'ready'"),
        "scaffold_runs": q("SELECT COUNT(*) FROM scaffold_runs"),
        "verification_runs": q("SELECT COUNT(*) FROM verification_runs"),
        "passing_verifications": q("SELECT COUNT(*) FROM verification_runs WHERE status = 'pass'"),
        "reviews": q("SELECT COUNT(*) FROM review_records"),
        "submissions": q("SELECT COUNT(*) FROM submissions"),
        "published": q("SELECT COUNT(*) FROM publish_records WHERE status IN ('published', 'no_changes')"),
        "learning_events": q("SELECT COUNT(*) FROM learning_events"),
        "latest_submissions": latest_submissions,
    }


def next_actions(conn, limit: int = 20) -> list[dict]:
    """Return controller-visible next steps without letting agents infer global state."""
    actions: list[dict] = []

    accepted_without_contract = conn.execute(
        "SELECT i.id, i.title FROM ideas i"
        " JOIN verdicts v ON v.idea_id = i.id"
        " LEFT JOIN task_contracts c ON c.idea_id = i.id"
        " WHERE v.verdict = 'accept' AND c.id IS NULL"
        " ORDER BY i.id LIMIT ?",
        (limit,),
    ).fetchall()
    for row in accepted_without_contract:
        actions.append(
            {
                "stage": "contract",
                "target": f"idea:{row['id']}",
                "action": f"synthtask contract create {row['id']}",
                "reason": "accepted idea has no task contract",
                "title": row["title"],
            }
        )

    remaining = max(limit - len(actions), 0)
    if remaining:
        draft_contracts = conn.execute(
            "SELECT * FROM task_contracts"
            " WHERE status = 'draft' ORDER BY updated_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in draft_contracts:
            missing = validate_contract(row)
            action = (
                f"fill contract #{row['id']} fields: {', '.join(missing)}"
                if missing
                else f"synthtask contract ready {row['id']}"
            )
            actions.append(
                {
                    "stage": "contract",
                    "target": f"contract:{row['id']}",
                    "action": action,
                    "reason": "draft contract is not ready for scaffolding",
                    "idea_id": row["idea_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        ready_without_scaffold = conn.execute(
            "SELECT c.id, c.idea_id FROM task_contracts c"
            " LEFT JOIN scaffold_runs s ON s.contract_id = c.id"
            " WHERE c.status = 'ready' AND s.id IS NULL"
            " ORDER BY c.updated_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in ready_without_scaffold:
            actions.append(
                {
                    "stage": "scaffold",
                    "target": f"contract:{row['id']}",
                    "action": f"synthtask scaffold start {row['id']} --builder codex",
                    "reason": "ready contract has no scaffold workspace",
                    "idea_id": row["idea_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        scaffolds_without_pass = conn.execute(
            "SELECT s.id, s.contract_id FROM scaffold_runs s"
            " WHERE NOT EXISTS ("
            "   SELECT 1 FROM verification_runs v"
            "   WHERE v.scaffold_run_id = s.id AND v.status = 'pass'"
            " )"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = s.id"
            " )"
            " ORDER BY s.started_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in scaffolds_without_pass:
            actions.append(
                {
                    "stage": "verify",
                    "target": f"scaffold:{row['id']}",
                    "action": f"synthtask verify run {row['id']} --cwd task -- <command>",
                    "reason": "scaffold has no passing verification",
                    "scaffold_run_id": row["id"],
                    "contract_id": row["contract_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        verified_without_review = conn.execute(
            "SELECT s.id, s.contract_id FROM scaffold_runs s"
            " WHERE EXISTS ("
            "   SELECT 1 FROM verification_runs v"
            "   WHERE v.scaffold_run_id = s.id AND v.status = 'pass'"
            " )"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM review_records r"
            "   WHERE r.scaffold_run_id = s.id AND r.verdict = 'approve'"
            " )"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = s.id"
            " )"
            " ORDER BY s.started_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in verified_without_review:
            actions.append(
                {
                    "stage": "audit",
                    "target": f"scaffold:{row['id']}",
                    "action": f"synthtask audit record {row['id']} --reviewer <name> --verdict approve",
                    "reason": "verified scaffold has no approving adversarial review",
                    "scaffold_run_id": row["id"],
                    "contract_id": row["contract_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        approved_without_promote = conn.execute(
            "SELECT s.id, s.contract_id FROM scaffold_runs s"
            " WHERE s.canonical_root IS NULL"
            " AND EXISTS ("
            "   SELECT 1 FROM review_records r"
            "   WHERE r.scaffold_run_id = s.id AND r.verdict = 'approve'"
            " )"
            " AND NOT EXISTS ("
            "   SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = s.id"
            " )"
            " ORDER BY s.started_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in approved_without_promote:
            actions.append(
                {
                    "stage": "promote",
                    "target": f"scaffold:{row['id']}",
                    "action": f"synthtask scaffold promote {row['id']} /path/to/canonical-task-root",
                    "reason": "approved scaffold has not been promoted to canonical task bytes",
                    "scaffold_run_id": row["id"],
                    "contract_id": row["contract_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        approved_without_publish = conn.execute(
            "SELECT s.id, s.contract_id FROM scaffold_runs s"
            " WHERE s.canonical_root IS NOT NULL"
            " AND EXISTS ("
            "   SELECT 1 FROM review_records r"
            "   WHERE r.scaffold_run_id = s.id AND r.verdict = 'approve'"
            " )"
            " AND NOT EXISTS (SELECT 1 FROM publish_records p WHERE p.scaffold_run_id = s.id)"
            " AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = s.id)"
            " ORDER BY s.started_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in approved_without_publish:
            actions.append(
                {
                    "stage": "publish",
                    "target": f"scaffold:{row['id']}",
                    "action": f"synthtask publish run {row['id']} --task-name <task-name>",
                    "reason": "approved scaffold has not been published to the task repo",
                    "scaffold_run_id": row["id"],
                    "contract_id": row["contract_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        published_without_submission = conn.execute(
            "SELECT p.scaffold_run_id, p.task_name, sr.contract_id FROM publish_records p"
            " JOIN ("
            "   SELECT scaffold_run_id, MAX(id) AS id"
            "   FROM publish_records"
            "   WHERE status IN ('published', 'no_changes')"
            "   GROUP BY scaffold_run_id"
            " ) latest ON latest.id = p.id"
            " JOIN scaffold_runs sr ON sr.id = p.scaffold_run_id"
            " WHERE NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = p.scaffold_run_id)"
            " ORDER BY p.created_at DESC, p.id DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in published_without_submission:
            actions.append(
                {
                    "stage": "smoldata",
                    "target": f"scaffold:{row['scaffold_run_id']}",
                    "action": f"synthtask smoldata watch {row['task_name']} --scaffold-run-id {row['scaffold_run_id']}",
                    "reason": "published task has no recorded Codimango validation result",
                    "scaffold_run_id": row["scaffold_run_id"],
                    "contract_id": row["contract_id"],
                    "task_name": row["task_name"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        unsettled = conn.execute(
            "SELECT sub.id, sub.scaffold_run_id, sub.status, sr.contract_id,"
            " COALESCE(NULLIF(sub.external_id, ''), ("
            "   SELECT p.task_name FROM publish_records p"
            "   WHERE p.scaffold_run_id = sub.scaffold_run_id"
            "     AND p.status IN ('published', 'no_changes')"
            "   ORDER BY p.id DESC LIMIT 1"
            " )) AS task_name"
            " FROM submissions sub"
            " JOIN ("
            "   SELECT scaffold_run_id, MAX(id) AS id"
            "   FROM submissions"
            "   GROUP BY scaffold_run_id"
            " ) latest ON latest.id = sub.id"
            " JOIN scaffold_runs sr ON sr.id = sub.scaffold_run_id"
            f" WHERE LOWER(sub.status) IN ({_marks(POLLABLE_SUBMISSION_STATUSES)})"
            " ORDER BY sub.updated_at DESC, sub.id DESC LIMIT ?",
            (*POLLABLE_SUBMISSION_STATUSES, remaining),
        ).fetchall()
        for row in unsettled:
            task_name = row["task_name"] or ""
            action = (
                f"synthtask smoldata watch {task_name} --scaffold-run-id {row['scaffold_run_id']}"
                if task_name
                else f"synthtask publish run {row['scaffold_run_id']} --task-name <task-name>"
            )
            actions.append(
                {
                    "stage": "poll",
                    "target": f"submission:{row['id']}",
                    "action": action,
                    "reason": f"Codimango status {row['status']!r} has not settled",
                    "scaffold_run_id": row["scaffold_run_id"],
                    "contract_id": row["contract_id"],
                    "task_name": task_name,
                    "route": triage_route(row["status"]),
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        unroutable = SETTLED_OK_SUBMISSION_STATUSES + POLLABLE_SUBMISSION_STATUSES
        latest_failed_submissions = conn.execute(
            "SELECT sub.id, sub.scaffold_run_id, sub.status, sr.contract_id"
            " FROM submissions sub"
            " JOIN ("
            "   SELECT scaffold_run_id, MAX(id) AS id"
            "   FROM submissions"
            "   GROUP BY scaffold_run_id"
            " ) latest ON latest.id = sub.id"
            " JOIN scaffold_runs sr ON sr.id = sub.scaffold_run_id"
            f" WHERE LOWER(sub.status) NOT IN ({_marks(unroutable)})"
            " ORDER BY sub.updated_at DESC, sub.id DESC LIMIT ?",
            (*unroutable, remaining),
        ).fetchall()
        for row in latest_failed_submissions:
            route = triage_route(row["status"])
            # `record_submission` captures the failure automatically now, so the revision
            # is always the next step rather than something gated on recording it first.
            action = f"synthtask scaffold start {row['contract_id']} --builder codex"
            actions.append(
                {
                    "stage": "triage",
                    "target": f"submission:{row['id']}",
                    "action": action,
                    "reason": f"latest Smoldata status routes to {route}",
                    "scaffold_run_id": row["scaffold_run_id"],
                    "contract_id": row["contract_id"],
                    "route": route,
                }
            )

    return actions[:limit]


def seed_from_bundle_payload(payload: dict) -> dict:
    """Best-effort bridge from graph discovery outputs to seed-like metadata."""
    files = payload.get("files", [])
    text = "\n\n".join(str(f.get("content", "")) for f in files)
    title = ""
    for line in text.splitlines():
        stripped = line.strip("# ")
        if stripped:
            title = stripped[:120]
            break
    return {
        "title": title or "Discovery Bundle",
        "slug": seeds.slugify(title or "discovery-bundle"),
    }
