"""Command line entry point: `synthtask <command>`."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import (
    db,
    dedup,
    generate,
    judge,
    lifecycle,
    orchestrator,
    publisher,
    report,
    seeds,
    smoldata,
    sweep,
)


def cmd_seed_search(args) -> int:
    results = seeds.search(args.query, args.limit, args.sort_by)
    if not results:
        print("no results")
        return 1
    for r in results:
        print(
            f"  [{r['arxiv_id']}] {r['year']}  cites={r['citations']:>4}  {r['title'][:88]}"
        )
    print(f"\nadd one with:  synthtask seed add --arxiv-id <ID> --lane {args.sort_by and 'llm-eval'}")
    return 0


def cmd_seed_add(args) -> int:
    conn = db.connect(args.db)
    seed_id, seed_dir = seeds.add(conn, args.arxiv_id, lane=args.lane, notes=args.notes or "")
    print(f"seed #{seed_id} → {seed_dir}")
    print(f"  next: fill in {seed_dir / 'ASSUMPTIONS.md'} before generating")
    return 0


def cmd_seed_list(args) -> int:
    conn = db.connect(args.db)
    rows = db.list_seeds(conn)
    if not rows:
        print("no seeds yet — try `synthtask seed search \"...\"`")
        return 0
    for r in rows:
        n = conn.execute(
            "SELECT COUNT(*) FROM ideas WHERE seed_id = ?", (r["id"],)
        ).fetchone()[0]
        print(f"  #{r['id']:<3} {r['slug']:<52} {n:>3} ideas   {r['lane'] or '-'}")
    return 0


def cmd_generate(args) -> int:
    conn = db.connect(args.db)
    gens = args.generator.split(",") if args.generator != "both" else ["codex", "tbh"]
    rc = 0
    for gen in gens:
        print(f"→ {gen} on seed {args.seed} ({args.n} ideas)...", flush=True)
        try:
            run_id, n = generate.run(
                conn,
                args.seed,
                gen,
                n_ideas=args.n,
                model=args.model,
                timeout=args.timeout,
                prompt_version=args.prompt_version,
            )
            print(f"  run #{run_id}: {n} ideas persisted")
            if n == 0:
                print(f"  (no ideas parsed — inspect runs/…/stdout.log)")
                rc = 1
        except generate.GeneratorError as exc:
            print(f"  error: {exc}", file=sys.stderr)
            rc = 1
    if rc == 0:
        stats = dedup.scan(conn)
        print(f"prefilter: {stats['dupe_pairs']} dupe pairs, {stats['antipattern_hits']} stale-pattern hits")
    return rc


def cmd_dedup(args) -> int:
    conn = db.connect(args.db)
    stats = dedup.scan(conn, threshold=args.threshold)
    print(json.dumps(stats, indent=2))
    if args.adjudicate:
        print("escalating borderline pairs to Codex...")
        print(json.dumps(judge.adjudicate_dupes(conn, args.threshold), indent=2))
    return 0


def cmd_judge(args) -> int:
    conn = db.connect(args.db)
    try:
        print(json.dumps(judge.score_ideas(conn, args.seed, limit=args.limit), indent=2))
    except judge.JudgeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_review(args) -> int:
    conn = db.connect(args.db)
    from . import review

    review.loop(conn, args.seed)
    return 0


def cmd_report(args) -> int:
    conn = db.connect(args.db)
    print(report.as_json(conn) if args.json else report.render(conn))
    return 0


def cmd_outcome(args) -> int:
    conn = db.connect(args.db)
    fields = {}
    if args.smoldata_task_id:
        fields["smoldata_task_id"] = args.smoldata_task_id
        fields["submitted_at"] = __import__("time").time()
    if args.accepted is not None:
        fields["accepted"] = int(args.accepted)
    if args.pass_rate is not None:
        fields["pass_rate"] = args.pass_rate
    if args.revisions is not None:
        fields["revisions"] = args.revisions
    if args.scaffolded:
        fields["scaffolded"] = 1
    if not fields:
        print("nothing to record", file=sys.stderr)
        return 1
    db.set_outcome(conn, args.idea_id, **fields)
    print(f"idea #{args.idea_id} outcome updated: {list(fields)}")
    return 0


def cmd_discovery_ingest(args) -> int:
    conn = db.connect(args.db)
    try:
        bundle_id = lifecycle.ingest_discovery_bundle(
            conn,
            Path(args.path),
            seed_ref=args.seed,
            source=args.source,
            source_url=args.source_url,
            title=args.title,
            bundle_key=args.bundle_key,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"discovery bundle #{bundle_id} ingested")
    return 0


def cmd_discovery_list(args) -> int:
    conn = db.connect(args.db)
    rows = db.list_discovery_bundles(conn)
    if not rows:
        print("no discovery bundles yet")
        return 0
    for r in rows:
        seed = f"seed #{r['seed_id']}" if r["seed_id"] is not None else "no seed"
        print(f"  #{r['id']:<3} {r['bundle_key']:<18} {seed:<10} {r['source']:<18} {r['title']}")
    return 0


def cmd_contract_create(args) -> int:
    conn = db.connect(args.db)
    overrides = {
        "objective": args.objective,
        "hidden_principle": args.hidden_principle,
        "allowed_inputs": json.dumps(args.allowed_input or []),
        "forbidden_leaks": json.dumps(args.forbidden_leak or []),
        "oracle_strategy": args.oracle_strategy,
        "mutation_strategy": args.mutation_strategy,
        "infra_requirements": args.infra_requirement,
        "difficulty_target": args.difficulty_target,
    }
    try:
        contract_id = lifecycle.create_contract(
            conn,
            args.idea_id,
            discovery_bundle_id=args.bundle_id,
            force=args.force,
            **overrides,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"contract #{contract_id} created")
    missing = lifecycle.validate_contract(db.get_task_contract(conn, contract_id))
    if missing:
        print("  status: draft")
        print(f"  missing for ready: {', '.join(missing)}")
    else:
        print(f"  status: readyable — run `synthtask contract ready {contract_id}`")
    return 0


def cmd_contract_list(args) -> int:
    conn = db.connect(args.db)
    rows = db.list_task_contracts(conn)
    if not rows:
        print("no task contracts yet")
        return 0
    for r in rows:
        print(
            f"  #{r['id']:<3} idea #{r['idea_id']:<3} v{r['version']:<2} "
            f"{r['status']:<7} {r['idea_title'][:80]}"
        )
    return 0


def cmd_contract_show(args) -> int:
    conn = db.connect(args.db)
    row = db.get_task_contract(conn, args.contract_id)
    if row is None:
        print(f"error: no contract #{args.contract_id}", file=sys.stderr)
        return 1
    obj = lifecycle.contract_dict(row)
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0


def cmd_contract_ready(args) -> int:
    conn = db.connect(args.db)
    try:
        missing = lifecycle.mark_contract_ready(conn, args.contract_id)
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if missing:
        print(f"contract #{args.contract_id} is not ready; missing: {', '.join(missing)}")
        return 1
    print(f"contract #{args.contract_id} marked ready")
    return 0


def cmd_contract_shelve(args) -> int:
    conn = db.connect(args.db)
    if db.get_task_contract(conn, args.contract_id) is None:
        print(f"error: no contract #{args.contract_id}", file=sys.stderr)
        return 1
    db.update_task_contract_status(conn, args.contract_id, "shelved")
    print(f"contract #{args.contract_id} shelved")
    return 0


def cmd_scaffold_start(args) -> int:
    conn = db.connect(args.db)
    try:
        scaffold_id, root = lifecycle.start_scaffold(
            conn,
            args.contract_id,
            builder=args.builder,
            model=args.model or "",
            revision=args.revision,
            allow_draft=args.allow_draft,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"scaffold run #{scaffold_id} started")
    print(f"  workspace: {root}")
    print(f"  build task files under: {root / 'task'}")
    return 0


def cmd_scaffold_list(args) -> int:
    conn = db.connect(args.db)
    rows = db.list_scaffold_runs(conn)
    if not rows:
        print("no scaffold runs yet")
        return 0
    for r in rows:
        print(
            f"  #{r['id']:<3} contract #{r['contract_id']:<3} r{r['revision']:<2} "
            f"{r['builder']:<8} {r['state']:<9} {r['idea_title'][:70]}"
        )
    return 0


def cmd_scaffold_promote(args) -> int:
    conn = db.connect(args.db)
    try:
        lifecycle.promote_scaffold(conn, args.scaffold_run_id, Path(args.canonical_root))
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"scaffold run #{args.scaffold_run_id} promoted to {args.canonical_root}")
    return 0


def cmd_scaffold_run(args) -> int:
    conn = db.connect(args.db)
    try:
        rc = lifecycle.run_scaffold_worker(
            conn,
            args.scaffold_run_id,
            Path(args.prompt_file),
            timeout=args.timeout,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"scaffold run #{args.scaffold_run_id} worker exit code: {rc}")
    return 0 if rc == 0 else 1


def cmd_verify_run(args) -> int:
    command = args.command
    cwd = args.cwd
    verifier = args.verifier
    timeout = args.timeout
    while command and command[0] != "--":
        if command[0] == "--cwd" and len(command) >= 2:
            cwd = command[1]
            command = command[2:]
        elif command[0] == "--verifier" and len(command) >= 2:
            verifier = command[1]
            command = command[2:]
        elif command[0] == "--timeout" and len(command) >= 2:
            timeout = int(command[1])
            command = command[2:]
        else:
            break
    if command and command[0] == "--":
        command = command[1:]
    conn = db.connect(args.db)
    try:
        verify_id = lifecycle.run_verification(
            conn,
            args.scaffold_run_id,
            command,
            verifier=verifier,
            cwd_choice=cwd,
            timeout=timeout,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    row = conn.execute("SELECT status FROM verification_runs WHERE id = ?", (verify_id,)).fetchone()
    print(f"verification #{verify_id}: {row['status']}")
    return 0 if row["status"] == "pass" else 1


def cmd_verify_record(args) -> int:
    conn = db.connect(args.db)
    verify_id = db.add_verification_run(
        conn,
        scaffold_run_id=args.scaffold_run_id,
        verifier=args.verifier,
        command=args.command,
        status=args.status,
        stdout_tail=args.stdout_tail,
        stderr_tail=args.stderr_tail,
    )
    print(f"verification #{verify_id} recorded: {args.status}")
    return 0 if args.status == "pass" else 1


def cmd_audit_record(args) -> int:
    conn = db.connect(args.db)
    issues = []
    for item in args.issue or []:
        if ":" in item:
            code, detail = item.split(":", 1)
        else:
            code, detail = item, ""
        issues.append({"code": code.strip(), "detail": detail.strip()})
    try:
        review_id = lifecycle.record_review(
            conn,
            args.scaffold_run_id,
            reviewer=args.reviewer,
            kind=args.kind,
            verdict=args.verdict,
            issues=issues,
            note=args.note,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"review #{review_id} recorded: {args.verdict}")
    return 0 if args.verdict == "approve" else 1


def cmd_submission_record(args) -> int:
    conn = db.connect(args.db)
    result = {}
    if args.result_json:
        try:
            result = json.loads(args.result_json)
        except json.JSONDecodeError as exc:
            print(f"error: invalid --result-json: {exc}", file=sys.stderr)
            return 1
    try:
        submission_id = lifecycle.record_submission(
            conn,
            args.scaffold_run_id,
            platform=args.platform,
            external_id=args.external_id or "",
            status=args.status,
            pass_rate=args.pass_rate,
            revisions=args.revisions,
            result=result,
        )
    except lifecycle.LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"submission #{submission_id} recorded: {args.status} "
        f"(next: {lifecycle.triage_route(args.status)})"
    )
    return 0


def cmd_publish_run(args) -> int:
    conn = db.connect(args.db)
    try:
        record_id = publisher.publish_scaffold(
            conn,
            args.scaffold_run_id,
            task_name=args.task_name or None,
            remote_url=args.remote or None,
            branch=args.branch,
            message=args.message or "",
            push=not args.no_push,
            overwrite=args.overwrite,
            method=args.method,
        )
    except publisher.PublishError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    row = conn.execute("SELECT * FROM publish_records WHERE id = ?", (record_id,)).fetchone()
    payload = json.loads(row["payload_json"])
    print(f"publish #{record_id}: {row['status']} {row['task_name']}")
    if payload.get("github_url"):
        print(f"  github: {payload['github_url']}")
    print(f"  remote: {row['remote_url']} ({row['branch']})")
    print(f"  method: {payload.get('method', 'git')}")
    print(f"  inventory_sha256: {payload.get('inventory_sha256', '-')}")
    return 0


def cmd_publish_list(args) -> int:
    conn = db.connect(args.db)
    rows = conn.execute(
        "SELECT * FROM publish_records ORDER BY created_at DESC, id DESC LIMIT ?",
        (args.limit,),
    ).fetchall()
    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print("no publish records yet")
        return 0
    for row in rows:
        sha = (row["commit_sha"] or "")[:12] or "-"
        print(
            f"  #{row['id']:<3} scaffold #{row['scaffold_run_id']:<3} "
            f"{row['status']:<10} {row['task_name']:<48} {sha}"
        )
        if row["github_url"]:
            print(f"      {row['github_url']}")
    return 0


def cmd_learn_add(args) -> int:
    conn = db.connect(args.db)
    payload = {}
    if args.payload_json:
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError as exc:
            print(f"error: invalid --payload-json: {exc}", file=sys.stderr)
            return 1
    event_id = lifecycle.record_learning(
        conn,
        scope_type=args.scope_type,
        scope_id=args.scope_id,
        label=args.label,
        detail=args.detail,
        payload=payload,
    )
    print(f"learning event #{event_id} recorded")
    return 0


def cmd_pipeline_status(args) -> int:
    conn = db.connect(args.db)
    payload = {
        "summary": lifecycle.pipeline_summary(conn),
        "next_actions": lifecycle.next_actions(conn, limit=args.limit),
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    s = payload["summary"]
    print("TASK-GENERATION PIPELINE")
    print("═" * 62)
    print(
        f"  bundles {s['discovery_bundles']}   contracts {s['contracts']}"
        f"   ready {s['ready_contracts']}   scaffolds {s['scaffold_runs']}"
    )
    print(
        f"  verifications {s['verification_runs']}   reviews {s['reviews']}"
        f"   published {s['published']}   submissions {s['submissions']}"
        f"   learnings {s['learning_events']}"
    )
    print("")
    print("NEXT ACTIONS")
    print("─" * 62)
    if not payload["next_actions"]:
        print("  no queued actions")
    for item in payload["next_actions"]:
        print(f"  [{item['stage']}] {item['target']}: {item['reason']}")
        print(f"      {item['action']}")
    return 0


def cmd_pipeline_run(args) -> int:
    verify_commands = [orchestrator.parse_command(cmd) for cmd in args.verify_command]
    overrides = {
        "objective": args.objective,
        "hidden_principle": args.hidden_principle,
        "allowed_inputs": json.dumps(args.allowed_input or []),
        "forbidden_leaks": json.dumps(args.forbidden_leak or []),
        "oracle_strategy": args.oracle_strategy,
        "mutation_strategy": args.mutation_strategy,
        "infra_requirements": args.infra_requirement,
        "difficulty_target": args.difficulty_target,
    }
    conn = db.connect(args.db)
    config = orchestrator.PipelineRunConfig(
        idea_id=args.idea_id,
        contract_id=args.contract_id,
        scaffold_run_id=args.scaffold_run_id,
        bundle_id=args.bundle_id,
        builder=args.builder,
        model=args.model or "",
        build_prompt_file=Path(args.build_prompt_file) if args.build_prompt_file else None,
        verify_commands=verify_commands,
        canonical_root=Path(args.canonical_root) if args.canonical_root else None,
        publish_task_name=args.publish_task_name or "",
        publish_remote=args.publish_remote or "",
        publish_branch=args.publish_branch,
        publish_message=args.publish_message or "",
        publish_push=not args.no_push,
        publish_overwrite=args.overwrite_publish,
        publish_method=args.publish_method,
        smoldata_task_name=args.smoldata_task_name or "",
        smoldata_site=args.smoldata_site,
        source_repo=args.source_repo or "",
        stop_after=args.stop_after,
        force_contract=args.force_contract,
        allow_draft_scaffold=args.allow_draft_scaffold,
        allow_build=not args.no_build,
        contract_overrides=overrides,
    )
    try:
        result = orchestrator.run(conn, config)
    except orchestrator.OrchestratorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    return 1 if result.blocked_at else 0


def _settings_row_dict(row) -> dict:
    data = {k: row[k] for k in db.CONTRACT_SETTING_FIELDS}
    data["contract_id"] = row["contract_id"]
    data["auto_advance"] = bool(row["auto_advance"])
    data["verify_commands"] = json.loads(row["verify_commands"] or "[]")
    return data


def cmd_settings_set(args) -> int:
    conn = db.connect(args.db)
    if db.get_task_contract(conn, args.contract_id) is None:
        print(f"error: no contract #{args.contract_id}", file=sys.stderr)
        return 1

    updates: dict = {}
    if args.verify_command:
        for command in args.verify_command:
            orchestrator.parse_command(command)  # reject unparseable early
        updates["verify_commands"] = json.dumps(args.verify_command)
    if args.canonical_root is not None:
        updates["canonical_root"] = str(Path(args.canonical_root).expanduser())
    for attr in (
        "publish_task_name",
        "publish_remote",
        "publish_branch",
        "publish_method",
        "smoldata_site",
        "source_repo",
    ):
        value = getattr(args, attr)
        if value is not None:
            updates[attr] = value
    if args.auto_advance is not None:
        updates["auto_advance"] = int(args.auto_advance)

    db.set_contract_settings(conn, args.contract_id, **updates)
    print(json.dumps(_settings_row_dict(db.get_contract_settings(conn, args.contract_id)), indent=2))
    return 0


def cmd_settings_show(args) -> int:
    conn = db.connect(args.db)
    row = db.get_contract_settings(conn, args.contract_id)
    if row is None:
        print(f"contract #{args.contract_id} has no stored settings")
        return 1
    print(json.dumps(_settings_row_dict(row), indent=2))
    return 0


def cmd_settings_list(args) -> int:
    conn = db.connect(args.db)
    rows = [_settings_row_dict(r) for r in db.list_contract_settings(conn)]
    print(json.dumps(rows, indent=2))
    return 0


def cmd_sweep(args) -> int:
    conn = db.connect(args.db)
    try:
        with sweep.exclusive_lock():
            summary = sweep.run(conn, dry_run=args.dry_run, limit=args.limit)
    except sweep.SweepError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2) if args.json else sweep.format_summary(summary))
    # Blocked tasks are the normal resting state, so only harness faults are non-zero.
    return 1 if summary["errors"] else 0


def cmd_smoldata_show(args) -> int:
    try:
        payload = smoldata.show_task(args.task_name, site=args.site, timeout=args.timeout)
    except smoldata.SmoldataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_smoldata_watch(args) -> int:
    conn = db.connect(args.db)
    try:
        payload = smoldata.watch_task(args.task_name, site=args.site, timeout=args.timeout)
    except smoldata.SmoldataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.scaffold_run_id:
        record = smoldata.submission_record(
            args.task_name,
            status=payload["status"],
            payload={"watch": payload.get("payload")},
        )
        lifecycle.record_submission(conn, args.scaffold_run_id, **record)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_smoldata_review(args) -> int:
    conn = db.connect(args.db)
    try:
        payload = smoldata.agentic_review(
            args.task_name,
            site=args.site,
            source_repo=args.source_repo or "",
            wait=args.wait,
            fail_on_bad=args.fail_on_bad,
            timeout=args.timeout,
        )
    except smoldata.SmoldataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.scaffold_run_id:
        record = smoldata.submission_record(
            args.task_name,
            status=payload["status"],
            payload={"review": payload.get("payload")},
        )
        lifecycle.record_submission(conn, args.scaffold_run_id, **record)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if payload.get("status") == "pending":
        return 0
    return payload.get("returncode", 0)


def cmd_smoldata_rerun(args) -> int:
    try:
        payload = smoldata.rerun_task(args.task_name, site=args.site, timeout=args.timeout)
    except smoldata.SmoldataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="synthtask", description=__doc__)
    p.add_argument("--db", default=None, help="path to the pipeline SQLite DB")
    sub = p.add_subparsers(dest="cmd", required=True)

    seed = sub.add_parser("seed", help="manage paper seeds").add_subparsers(
        dest="seedcmd", required=True
    )

    s1 = seed.add_parser("search", help="search arXiv via `meta search.paper`")
    s1.add_argument("query")
    s1.add_argument("--limit", type=int, default=10)
    s1.add_argument(
        "--sort-by", default="relevance",
        choices=["relevance", "citations", "recency", "composite"],
    )
    s1.set_defaults(func=cmd_seed_search)

    s2 = seed.add_parser("add", help="ingest a paper by arXiv id")
    s2.add_argument("--arxiv-id", required=True)
    s2.add_argument("--lane", default="")
    s2.add_argument("--notes", default="")
    s2.set_defaults(func=cmd_seed_add)

    s3 = seed.add_parser("list", help="list ingested seeds")
    s3.set_defaults(func=cmd_seed_list)

    g = sub.add_parser("generate", help="generate ideas under isolation")
    g.add_argument("seed", help="seed slug or arXiv id")
    g.add_argument("--generator", default="both", help="codex | tbh | both")
    g.add_argument("-n", type=int, default=8, help="ideas per generator")
    g.add_argument("--model", default=None)
    g.add_argument("--timeout", type=int, default=1800)
    g.add_argument("--prompt-version", default="v1")
    g.set_defaults(func=cmd_generate)

    d = sub.add_parser("dedup", help="lexical + stale-pattern prefilter")
    d.add_argument("--threshold", type=float, default=0.45,
                   help="lexical dupe cutoff; lower it for terse idea statements")
    d.add_argument("--adjudicate", action="store_true", help="escalate pairs to Codex")
    d.set_defaults(func=cmd_dedup)

    j = sub.add_parser("judge", help="score ideas with Codex against your rubric")
    j.add_argument("--seed", default=None)
    j.add_argument("--limit", type=int, default=None)
    j.set_defaults(func=cmd_judge)

    r = sub.add_parser("review", help="human review gate")
    r.add_argument("--seed", default=None)
    r.set_defaults(func=cmd_review)

    rp = sub.add_parser("report", help="corpus metrics")
    rp.add_argument("--json", action="store_true")
    rp.set_defaults(func=cmd_report)

    o = sub.add_parser("outcome", help="record what happened downstream")
    o.add_argument("idea_id", type=int)
    o.add_argument("--smoldata-task-id")
    o.add_argument("--accepted", type=int, choices=[0, 1], default=None)
    o.add_argument("--pass-rate", type=float, default=None)
    o.add_argument("--revisions", type=int, default=None)
    o.add_argument("--scaffolded", action="store_true")
    o.set_defaults(func=cmd_outcome)

    disc = sub.add_parser("discovery", help="manage graph-discovery bundles").add_subparsers(
        dest="discoverycmd", required=True
    )
    di = disc.add_parser("ingest", help="ingest a Paper Factory or graph-discovery bundle")
    di.add_argument("path")
    di.add_argument("--seed", default=None, help="optional seed slug, arXiv id, or id")
    di.add_argument("--source", default="graph-discovery")
    di.add_argument("--source-url", default="")
    di.add_argument("--title", default="")
    di.add_argument("--bundle-key", default="")
    di.set_defaults(func=cmd_discovery_ingest)

    dl = disc.add_parser("list", help="list ingested discovery bundles")
    dl.set_defaults(func=cmd_discovery_list)

    contract = sub.add_parser("contract", help="manage downstream task contracts").add_subparsers(
        dest="contractcmd", required=True
    )
    cc = contract.add_parser("create", help="draft a task contract from an accepted idea")
    cc.add_argument("idea_id", type=int)
    cc.add_argument("--bundle-id", type=int, default=None)
    cc.add_argument("--force", action="store_true", help="allow non-accepted ideas")
    cc.add_argument("--objective", default=None)
    cc.add_argument("--hidden-principle", default=None)
    cc.add_argument("--allowed-input", action="append", default=[])
    cc.add_argument("--forbidden-leak", action="append", default=[])
    cc.add_argument("--oracle-strategy", default=None)
    cc.add_argument("--mutation-strategy", default=None)
    cc.add_argument("--infra-requirement", default=None)
    cc.add_argument("--difficulty-target", default=None)
    cc.set_defaults(func=cmd_contract_create)

    cl = contract.add_parser("list", help="list task contracts")
    cl.set_defaults(func=cmd_contract_list)

    cs = contract.add_parser("show", help="print a task contract")
    cs.add_argument("contract_id", type=int)
    cs.add_argument("--json", action="store_true")
    cs.set_defaults(func=cmd_contract_show)

    cr = contract.add_parser("ready", help="mark a complete task contract ready")
    cr.add_argument("contract_id", type=int)
    cr.set_defaults(func=cmd_contract_ready)

    csh = contract.add_parser("shelve", help="shelve a task contract")
    csh.add_argument("contract_id", type=int)
    csh.set_defaults(func=cmd_contract_shelve)

    scaffold = sub.add_parser("scaffold", help="manage scaffold workspaces").add_subparsers(
        dest="scaffoldcmd", required=True
    )
    ss = scaffold.add_parser("start", help="create an isolated scaffold workspace")
    ss.add_argument("contract_id", type=int)
    ss.add_argument("--builder", default="manual", help="manual | codex | tbh | avocado")
    ss.add_argument("--model", default="")
    ss.add_argument("--revision", type=int, default=None)
    ss.add_argument("--allow-draft", action="store_true", help="start before the contract is ready")
    ss.set_defaults(func=cmd_scaffold_start)

    sl = scaffold.add_parser("list", help="list scaffold runs")
    sl.set_defaults(func=cmd_scaffold_list)

    srn = scaffold.add_parser("run", help="run the scaffold's builder inside its workspace")
    srn.add_argument("scaffold_run_id", type=int)
    srn.add_argument("--prompt-file", required=True, help="human-owned builder prompt template")
    srn.add_argument("--timeout", type=int, default=3600)
    srn.set_defaults(func=cmd_scaffold_run)

    sp = scaffold.add_parser("promote", help="copy staged task files into an empty canonical root")
    sp.add_argument("scaffold_run_id", type=int)
    sp.add_argument("canonical_root")
    sp.set_defaults(func=cmd_scaffold_promote)

    verify = sub.add_parser("verify", help="run or record scaffold verification").add_subparsers(
        dest="verifycmd", required=True
    )
    vr = verify.add_parser("run", help="run a verifier command and record the result")
    vr.add_argument("scaffold_run_id", type=int)
    vr.add_argument("--verifier", default="local")
    vr.add_argument("--cwd", choices=["workspace", "task", "canonical"], default="workspace")
    vr.add_argument("--timeout", type=int, default=1800)
    vr.add_argument("command", nargs=argparse.REMAINDER)
    vr.set_defaults(func=cmd_verify_run)

    vrec = verify.add_parser("record", help="record an external verifier result")
    vrec.add_argument("scaffold_run_id", type=int)
    vrec.add_argument("--verifier", default="external")
    vrec.add_argument("--command", required=True)
    vrec.add_argument("--status", required=True, choices=["pass", "fail", "timeout", "infra"])
    vrec.add_argument("--stdout-tail", default="")
    vrec.add_argument("--stderr-tail", default="")
    vrec.set_defaults(func=cmd_verify_record)

    audit = sub.add_parser("audit", help="record adversarial scaffold reviews").add_subparsers(
        dest="auditcmd", required=True
    )
    ar = audit.add_parser("record", help="record a reviewer verdict")
    ar.add_argument("scaffold_run_id", type=int)
    ar.add_argument("--reviewer", required=True)
    ar.add_argument("--kind", default="adversarial")
    ar.add_argument("--verdict", required=True, choices=["approve", "revise", "reject"])
    ar.add_argument("--issue", action="append", default=[])
    ar.add_argument("--note", default="")
    ar.set_defaults(func=cmd_audit_record)

    submission = sub.add_parser("submission", help="record validation results").add_subparsers(
        dest="submissioncmd", required=True
    )
    sr = submission.add_parser("record", help="record Smoldata/Codimango status")
    sr.add_argument("scaffold_run_id", type=int)
    sr.add_argument("--platform", required=True, choices=["smoldata", "codimango", "local"])
    sr.add_argument("--external-id", default="")
    sr.add_argument("--status", required=True)
    sr.add_argument("--pass-rate", type=float, default=None)
    sr.add_argument("--revisions", type=int, default=None)
    sr.add_argument("--result-json", default="")
    sr.set_defaults(func=cmd_submission_record)

    publish_cmd = sub.add_parser(
        "publish",
        help="publish promoted tasks to the Codimango-ingested repo",
    ).add_subparsers(dest="publishcmd", required=True)
    prun = publish_cmd.add_parser(
        "run",
        help="copy a promoted scaffold into the task repo and push",
    )
    prun.add_argument("scaffold_run_id", type=int)
    prun.add_argument(
        "--task-name",
        default="",
        help="top-level task directory name; defaults to canonical root name",
    )
    prun.add_argument(
        "--remote",
        default="",
        help="task repo remote; defaults to SYNTH_TASK_REMOTE or sibling ananyajain-tbench",
    )
    prun.add_argument("--branch", default=publisher.DEFAULT_BRANCH)
    prun.add_argument("--message", default="")
    prun.add_argument("--method", default="auto", choices=["auto", "git", "github-api"])
    prun.add_argument("--no-push", action="store_true", help="commit in a temp clone without pushing")
    prun.add_argument("--overwrite", action="store_true", help="replace an existing task directory")
    prun.set_defaults(func=cmd_publish_run)

    plist = publish_cmd.add_parser("list", help="list task-repo publication records")
    plist.add_argument("--json", action="store_true")
    plist.add_argument("--limit", type=int, default=20)
    plist.set_defaults(func=cmd_publish_list)

    learn = sub.add_parser("learn", help="record pipeline learning events").add_subparsers(
        dest="learncmd", required=True
    )
    la = learn.add_parser("add", help="add a learning event")
    la.add_argument("--scope-type", required=True)
    la.add_argument("--scope-id", type=int, required=True)
    la.add_argument("--label", required=True)
    la.add_argument("--detail", required=True)
    la.add_argument("--payload-json", default="")
    la.set_defaults(func=cmd_learn_add)

    pipeline = sub.add_parser("pipeline", help="show controller state and next actions").add_subparsers(
        dest="pipelinecmd", required=True
    )
    ps = pipeline.add_parser("status", help="summarize downstream pipeline state")
    ps.add_argument("--json", action="store_true")
    ps.add_argument("--limit", type=int, default=20)
    ps.set_defaults(func=cmd_pipeline_status)

    pr = pipeline.add_parser("run", help="advance one task through the controller stages")
    pr.add_argument("--idea-id", type=int, default=None)
    pr.add_argument("--contract-id", type=int, default=None)
    pr.add_argument("--scaffold-run-id", type=int, default=None)
    pr.add_argument("--bundle-id", type=int, default=None)
    pr.add_argument("--builder", default="codex", help="codex | tbh")
    pr.add_argument("--model", default="")
    pr.add_argument("--build-prompt-file", default="")
    pr.add_argument("--verify-command", action="append", default=[])
    pr.add_argument("--canonical-root", default="")
    pr.add_argument("--publish-task-name", default="")
    pr.add_argument("--publish-remote", default="")
    pr.add_argument("--publish-branch", default=publisher.DEFAULT_BRANCH)
    pr.add_argument("--publish-message", default="")
    pr.add_argument(
        "--publish-method",
        default="auto",
        choices=["auto", "git", "github-api"],
    )
    pr.add_argument("--no-push", action="store_true")
    pr.add_argument("--overwrite-publish", action="store_true")
    pr.add_argument("--smoldata-task-name", default="")
    pr.add_argument("--smoldata-site", default="default", choices=["default", "nest", "vanilla"])
    pr.add_argument("--source-repo", default="")
    pr.add_argument("--stop-after", default="learn", choices=orchestrator.STAGES)
    pr.add_argument("--force-contract", action="store_true")
    pr.add_argument("--allow-draft-scaffold", action="store_true")
    pr.add_argument(
        "--no-build",
        action="store_true",
        help="block at `build` instead of invoking the builder on an unbuilt scaffold",
    )
    pr.add_argument("--objective", default=None)
    pr.add_argument("--hidden-principle", default=None)
    pr.add_argument("--allowed-input", action="append", default=[])
    pr.add_argument("--forbidden-leak", action="append", default=[])
    pr.add_argument("--oracle-strategy", default=None)
    pr.add_argument("--mutation-strategy", default=None)
    pr.add_argument("--infra-requirement", default=None)
    pr.add_argument("--difficulty-target", default=None)
    pr.set_defaults(func=cmd_pipeline_run)

    settings = sub.add_parser(
        "settings", help="per-contract run settings used by unattended sweeps"
    ).add_subparsers(dest="settingscmd", required=True)

    setset = settings.add_parser("set", help="set stored run settings for a contract")
    setset.add_argument("contract_id", type=int)
    setset.add_argument(
        "--verify-command",
        action="append",
        default=None,
        help="repeatable; replaces the stored list",
    )
    setset.add_argument("--canonical-root", default=None)
    setset.add_argument("--publish-task-name", default=None)
    setset.add_argument("--publish-remote", default=None)
    setset.add_argument("--publish-branch", default=None)
    setset.add_argument("--publish-method", default=None, choices=["auto", "git", "github-api"])
    setset.add_argument("--smoldata-site", default=None, choices=["default", "nest", "vanilla"])
    setset.add_argument("--source-repo", default=None)
    setset.add_argument(
        "--auto-advance",
        dest="auto_advance",
        action="store_true",
        default=None,
        help="let `synthtask sweep` advance this contract's scaffolds",
    )
    setset.add_argument(
        "--no-auto-advance", dest="auto_advance", action="store_false", default=None
    )
    setset.set_defaults(func=cmd_settings_set)

    setshow = settings.add_parser("show", help="print stored settings for a contract")
    setshow.add_argument("contract_id", type=int)
    setshow.set_defaults(func=cmd_settings_show)

    setlist = settings.add_parser("list", help="print stored settings for every contract")
    setlist.set_defaults(func=cmd_settings_list)

    sw = sub.add_parser(
        "sweep",
        help="poll unsettled validations and advance opted-in scaffolds (cron entry point)",
    )
    sw.add_argument("--dry-run", action="store_true")
    sw.add_argument("--limit", type=int, default=50)
    sw.add_argument("--json", action="store_true")
    sw.set_defaults(func=cmd_sweep)

    sd = sub.add_parser("smoldata", help="watch and import Smoldata/Codimango feedback").add_subparsers(
        dest="smoldata_cmd", required=True
    )
    sh = sd.add_parser("show", help="show a Smoldata/Codimango task")
    sh.add_argument("task_name")
    sh.add_argument("--site", default="default", choices=["default", "nest", "vanilla"])
    sh.add_argument("--timeout", type=int, default=900)
    sh.set_defaults(func=cmd_smoldata_show)

    sw = sd.add_parser("watch", help="watch validation and optionally record the result")
    sw.add_argument("task_name")
    sw.add_argument("--site", default="default", choices=["default", "nest", "vanilla"])
    sw.add_argument("--timeout", type=int, default=3600)
    sw.add_argument("--scaffold-run-id", type=int, default=None)
    sw.set_defaults(func=cmd_smoldata_watch)

    srv = sd.add_parser("review", help="fetch Agentic Full-Task Review")
    srv.add_argument("task_name")
    srv.add_argument("--site", default="default", choices=["default", "nest", "vanilla"])
    srv.add_argument("--source-repo", default="")
    srv.add_argument("--wait", action="store_true")
    srv.add_argument("--fail-on-bad", action="store_true")
    srv.add_argument("--timeout", type=int, default=3600)
    srv.add_argument("--scaffold-run-id", type=int, default=None)
    srv.set_defaults(func=cmd_smoldata_review)

    srr = sd.add_parser("rerun", help="request validation rerun")
    srr.add_argument("task_name")
    srr.add_argument("--site", default="default", choices=["default", "nest", "vanilla"])
    srr.add_argument("--timeout", type=int, default=900)
    srr.set_defaults(func=cmd_smoldata_rerun)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
