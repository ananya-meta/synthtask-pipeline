"""Populate a throwaway corpus and render the report.

For demoing the pipeline before real generation has run — the Show & Tell artifact.
Writes to a temp DB, never touches data/ideation.db.

    python3 tools/demo_corpus.py
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from ideation import db, dedup, report  # noqa: E402

# Shaped after NG Li's reported split: Codex ideas mostly survive review, TBH ideas
# mostly land on the documented attractors.
CODEX_IDEAS = [
    ("kappa-deflating judge harness",
     "Rebuild the agreement calculation so chance-corrected and exact-match scores "
     "diverge measurably under position swaps.",
     "the paper assumes judges are order-invariant"),
    ("position-bias audit under renegotiation",
     "Detect a judge whose verdict flips when the two candidate responses are swapped, "
     "across a held-out cohort.",
     "assumes a stable pairwise ordering"),
    ("test-retest harness for stochastic judges",
     "Quantify judge self-consistency when temperature is nonzero and the rubric is "
     "unchanged.",
     "assumes deterministic decoding"),
    ("rubric bank collision detector",
     "Find rubric pairs that induce contradictory verdicts on the same response.",
     "assumes rubrics are mutually consistent"),
    ("verbosity-controlled reward model probe",
     "Isolate length effects from quality effects in a reward model's preference ordering.",
     "assumes verbosity bias is negligible"),
    ("cross-benchmark rank stability",
     "Measure how far judge rankings move across three benchmarks with disjoint prompt "
     "distributions.",
     "assumes ranking transfers across benchmarks"),
]

TBH_IDEAS = [
    ("reduce memory in the judge pipeline",
     "Rebuild the evaluation loop so it fits within a strict memory budget.", "unbounded RAM"),
    ("lower memory footprint for batch scoring",
     "Cut peak memory usage of the batch scoring pass under load.", "unbounded RAM"),
    ("speed up the judging loop",
     "Maximize throughput of the judge over a large evaluation set.", "assumes latency is free"),
    ("judge under token limit",
     "Score responses while staying under a strict token budget per call.",
     "assumes unlimited context window"),
    ("reimplement the validation protocol",
     "Reproduce the paper's Minimum Viable Validation Protocol end to end.", "none"),
    ("agreement metric with partial credit",
     "Build a scoring formula giving partial credit for near-miss verdicts.",
     "assumes binary agreement"),
]

VERDICTS = {
    1: ("accept", "ACCEPT"), 2: ("accept", "ACCEPT"), 3: ("accept", "ACCEPT_WITH_EDIT"),
    4: ("reject", "NOT_VERIFIABLE"), 5: ("accept", "ACCEPT"), 6: ("reject", "TOO_EASY"),
    7: ("reject", "STALE_PATTERN"), 8: ("reject", "DUPLICATE"), 9: ("reject", "STALE_PATTERN"),
    10: ("reject", "STALE_PATTERN"), 11: ("reject", "PAPER_REIMPL"),
    12: ("reject", "TOO_ARTIFICIAL"),
}

# Judge composites, deliberately imperfect: idea 6 scores mid but the human rejected it,
# so agreement lands below 1.0 the way a real rubric does.
JUDGE = {1: 4.4, 2: 4.1, 3: 3.8, 4: 2.6, 5: 4.3, 6: 3.9,
         7: 1.9, 8: 2.2, 9: 1.7, 10: 2.0, 11: 1.4, 12: 2.9}


def build(conn) -> None:
    seed_id = db.add_seed(
        conn, arxiv_id="2606.19544", slug="01-reliability-without-validity",
        title="Reliability without Validity", abstract="…", url="…", lane="llm-eval",
    )
    for gen, ideas in (("codex", CODEX_IDEAS), ("tbh", TBH_IDEAS)):
        run_id = db.start_run(conn, seed_id=seed_id, generator=gen, model="",
                              prompt_version="v1", isolation_root=f"/tmp/{gen}")
        for title, statement, assumption in ideas:
            db.add_idea(conn, run_id, seed_id, {
                "title": title, "statement": statement, "assumption_broken": assumption
            })
        db.finish_run(conn, run_id, 0, len(ideas))

    dedup.scan(conn)

    for idea_id, (verdict, code) in VERDICTS.items():
        db.add_verdict(conn, idea_id, verdict, code)
        m = JUDGE[idea_id]
        db.add_score(conn, idea_id, "rub-a1b2c3", "codex", novelty=m, feasibility=m,
                     difficulty=m, interestingness=m, verifiability=m, rationale="")

    db.set_outcome(conn, 1, scaffolded=1, submitted_at=1.0, smoldata_task_id="a-1",
                   accepted=1, pass_rate=0.13, revisions=4)
    db.set_outcome(conn, 2, scaffolded=1, submitted_at=1.0, smoldata_task_id="a-2",
                   accepted=0, pass_rate=0.80, revisions=7)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        conn = db.connect(pathlib.Path(tmp) / "demo.db")
        build(conn)
        print(report.render(conn))
