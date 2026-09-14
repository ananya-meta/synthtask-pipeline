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

SCAFFOLD_ALLOWED = {
    "TASK_CONTRACT.json",
    "TASK_CONTRACT.md",
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
    "infra": "fix_infra",
    "infra_error": "fix_infra",
    "bad_grading_weak": "strengthen_oracle",
    "grading_wrong": "fix_verifier_contract",
    "too_easy": "reduce_leakage_or_add_hidden_state",
    "too_hard": "simplify_or_retarget",
    "leak": "separate_visible_task_from_hidden_scoring",
    "timeout": "reduce_runtime_or_budget",
    "rejected": "triage_feedback",
}


class LifecycleError(RuntimeError):
    pass


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


def validate_contract(row) -> list[str]:
    missing = []
    for field in CONTRACT_FIELDS:
        value = (row[field] or "").strip()
        if not value or value.startswith("TODO"):
            missing.append(field)
    for field in ("allowed_inputs", "forbidden_leaks"):
        try:
            parsed = json.loads(row[field])
        except json.JSONDecodeError:
            missing.append(f"{field}:invalid_json")
            continue
        if not parsed:
            missing.append(field)
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


def _render_scaffold_prompt(template: str, root: Path) -> str:
    contract_json = (root / "TASK_CONTRACT.json").read_text(encoding="utf-8")
    contract_md = (root / "TASK_CONTRACT.md").read_text(encoding="utf-8")
    return (
        template.replace("{{TASK_CONTRACT_JSON}}", contract_json)
        .replace("{{TASK_CONTRACT_MD}}", contract_md)
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
    root = Path(scaffold["workspace_root"])
    prompt = _render_scaffold_prompt(prompt_path.read_text(encoding="utf-8"), root)
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
        elif status in {"rejected", "bad_grading_weak", "grading_wrong", "too_easy", "too_hard"}:
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
    return submission_id


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
    return TRIAGE_ROUTE.get(status.lower().strip(), "manual_triage")


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
                    "contract_id": row["contract_id"],
                }
            )

    remaining = max(limit - len(actions), 0)
    if remaining:
        approved_without_submission = conn.execute(
            "SELECT s.id, s.contract_id FROM scaffold_runs s"
            " WHERE EXISTS ("
            "   SELECT 1 FROM review_records r"
            "   WHERE r.scaffold_run_id = s.id AND r.verdict = 'approve'"
            " )"
            " AND NOT EXISTS (SELECT 1 FROM submissions sub WHERE sub.scaffold_run_id = s.id)"
            " ORDER BY s.started_at DESC LIMIT ?",
            (remaining,),
        ).fetchall()
        for row in approved_without_submission:
            actions.append(
                {
                    "stage": "submission",
                    "target": f"scaffold:{row['id']}",
                    "action": f"synthtask submission record {row['id']} --platform smoldata --status pending",
                    "reason": "approved scaffold has no recorded validation result",
                    "contract_id": row["contract_id"],
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
