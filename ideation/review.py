"""Human review gate.

Rejections are the valuable output here, not the accepts. Every rejection carries a
reason code drawn from the failure modes the track has already documented, so the
corpus accumulates into a labelled dataset that judge.py is measured against.
"""

from __future__ import annotations

import textwrap

from . import db, dedup

# key -> (verdict, reason_code, blurb)
CODES: dict[str, tuple[str, str, str]] = {
    "a": ("accept", "ACCEPT", "good as stated — proceed to scaffolding"),
    "e": ("accept", "ACCEPT_WITH_EDIT", "good core, needs a framing edit"),
    "m": ("reject", "MEMORIZED", "textbook fix a model recalls rather than reasons to"),
    "p": ("reject", "PAPER_REIMPL", "just reimplements the paper; no assumption broken"),
    "d": ("reject", "DUPLICATE", "near-dupe of an idea already in the corpus"),
    "s": ("reject", "STALE_PATTERN", "known attractor (constrain memory, token limit, ...)"),
    "o": ("reject", "OVERSPEC_RISK", "can't be stated without leaking the solution"),
    "v": ("reject", "NOT_VERIFIABLE", "no clean binary oracle exists"),
    "t": ("reject", "TOO_EASY", "a frontier model solves this trivially"),
    "r": ("reject", "TOO_ARTIFICIAL", "difficulty is synthetic, not real"),
    "n": ("reject", "NEEDS_SYNTH_DATA", "no real dataset available"),
    "b": ("reject", "SCOPE_TOO_BIG", "doesn't fit a task budget"),
}

RULE = "─" * 78


def _wrap(text: str, indent: str = "  ") -> str:
    return "\n".join(
        textwrap.fill(line, 76, initial_indent=indent, subsequent_indent=indent) or indent
        for line in (text or "").splitlines()
    )


def _menu() -> str:
    accepts = [f"[{k}] {c[1]}" for k, c in CODES.items() if c[0] == "accept"]
    rejects = [f"[{k}] {c[1]}" for k, c in CODES.items() if c[0] == "reject"]
    lines = ["  " + "   ".join(accepts)]
    for i in range(0, len(rejects), 3):
        lines.append("  " + "   ".join(rejects[i : i + 3]))
    lines.append("  [?] full key   [Enter] skip   [q] quit")
    return "\n".join(lines)


def show(conn, row) -> None:
    seed = conn.execute("SELECT * FROM seeds WHERE id = ?", (row["seed_id"],)).fetchone()
    run = conn.execute("SELECT * FROM runs WHERE id = ?", (row["run_id"],)).fetchone()

    print(f"\n{RULE}")
    print(f"idea #{row['id']}  ·  seed {seed['slug']}  ·  generator {run['generator']}")
    print(RULE)
    print(f"\n  {row['title']}\n")
    print(_wrap(row["statement"]))
    if row["assumption_broken"]:
        print(f"\n  assumption broken:\n{_wrap(row['assumption_broken'], '    ')}")
    if row["dataset_ref"]:
        print(f"\n  dataset: {row['dataset_ref']}")
    if row["difficulty_claim"]:
        print(f"\n  claimed difficulty:\n{_wrap(row['difficulty_claim'], '    ')}")

    flags = db.dupes_for(conn, row["id"])
    if flags:
        print("\n  ⚑ prefilter flags:")
        for f in flags:
            if f["method"] == "antipattern":
                print(f"      stale pattern — {f['detail']}")
            else:
                print(
                    f"      {f['method']} sim={f['similarity']:.2f} vs #{f['matched_idea_id']}"
                    f" “{f['detail']}”"
                )

    score = db.score_for(conn, row["id"])
    if score:
        dims = ["novelty", "feasibility", "difficulty", "interestingness", "verifiability"]
        shown = " ".join(
            f"{d[:4]}={score[d]:.1f}" for d in dims if score[d] is not None
        )
        print(f"\n  judge ({score['judge']}, {score['rubric_version']}): {shown}")
        if score["rationale"]:
            print(_wrap(score["rationale"], "      "))
    print()


def loop(conn, seed_ref: str | None = None, rescan: bool = True) -> dict:
    if rescan:
        dedup.scan(conn)

    pending = db.unreviewed_ideas(conn, seed_ref)
    if not pending:
        print("Nothing to review — every idea in the corpus has a verdict.")
        return {"reviewed": 0, "skipped": 0}

    print(f"{len(pending)} idea(s) awaiting review.  [q] quits and saves.")
    reviewed = skipped = 0

    for i, row in enumerate(pending, 1):
        show(conn, row)
        print(f"  ({i}/{len(pending)})")
        print(_menu())

        while True:
            try:
                key = input("  > ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\ninterrupted — progress saved.")
                return {"reviewed": reviewed, "skipped": skipped}

            if key == "q":
                print(f"\nstopped. {reviewed} reviewed, {skipped} skipped.")
                return {"reviewed": reviewed, "skipped": skipped}
            if key == "":
                skipped += 1
                break
            if key == "?":
                for k, (verdict, code, blurb) in CODES.items():
                    print(f"    [{k}] {code:<18} {verdict:<6} — {blurb}")
                continue
            if key in CODES:
                verdict, code, _ = CODES[key]
                note = input("  note (optional) > ").strip()
                db.add_verdict(conn, row["id"], verdict, code, note)
                reviewed += 1
                break
            print("  unrecognised — [?] for the full key")

    print(f"\ndone. {reviewed} reviewed, {skipped} skipped.")
    return {"reviewed": reviewed, "skipped": skipped}
