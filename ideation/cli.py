"""Command line entry point: `ideation <command>`."""

from __future__ import annotations

import argparse
import json
import sys

from . import db, dedup, generate, judge, report, seeds


def cmd_seed_search(args) -> int:
    results = seeds.search(args.query, args.limit, args.sort_by)
    if not results:
        print("no results")
        return 1
    for r in results:
        print(
            f"  [{r['arxiv_id']}] {r['year']}  cites={r['citations']:>4}  {r['title'][:88]}"
        )
    print(f"\nadd one with:  ideation seed add --arxiv-id <ID> --lane {args.sort_by and 'llm-eval'}")
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
        print("no seeds yet — try `ideation seed search \"...\"`")
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ideation", description=__doc__)
    p.add_argument("--db", default=None, help="path to ideation.db")
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

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
