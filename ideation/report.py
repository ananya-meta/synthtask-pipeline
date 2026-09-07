"""Metrics over the ideation corpus.

The point of this module is that ideation stops being anecdotal. Diversity, per-generator
yield, and judge-vs-human agreement are all tracked per prompt/rubric version, so a change
to a prompt can be argued for with a number instead of a vibe.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict

from . import db, dedup, judge

BAR = "█"


def _bar(frac: float, width: int = 24) -> str:
    n = int(round(frac * width))
    return BAR * n + "·" * (width - n)


def summary(conn) -> dict:
    q = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    return {
        "seeds": q("SELECT COUNT(*) FROM seeds"),
        "runs": q("SELECT COUNT(*) FROM runs"),
        "ideas": q("SELECT COUNT(*) FROM ideas"),
        "reviewed": q("SELECT COUNT(*) FROM verdicts"),
        "accepted": q("SELECT COUNT(*) FROM verdicts WHERE verdict = 'accept'"),
        "scored": q("SELECT COUNT(DISTINCT idea_id) FROM scores"),
        "submitted": q("SELECT COUNT(*) FROM outcomes WHERE submitted_at IS NOT NULL"),
    }


def yield_by_generator(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT r.generator, r.prompt_version,"
        "       COUNT(i.id) AS ideas,"
        "       SUM(CASE WHEN v.verdict = 'accept' THEN 1 ELSE 0 END) AS accepted,"
        "       SUM(CASE WHEN v.idea_id IS NOT NULL THEN 1 ELSE 0 END) AS reviewed"
        " FROM runs r"
        " JOIN ideas i ON i.run_id = r.id"
        " LEFT JOIN verdicts v ON v.idea_id = i.id"
        " GROUP BY r.generator, r.prompt_version"
        " ORDER BY r.generator, r.prompt_version"
    ).fetchall()
    out = []
    for r in rows:
        reviewed = r["reviewed"] or 0
        out.append(
            {
                "generator": r["generator"],
                "prompt_version": r["prompt_version"],
                "ideas": r["ideas"],
                "reviewed": reviewed,
                "accepted": r["accepted"] or 0,
                "accept_rate": round((r["accepted"] or 0) / reviewed, 3) if reviewed else None,
            }
        )
    return out


def reason_histogram(conn) -> list[tuple[str, int]]:
    rows = conn.execute(
        "SELECT reason_code, COUNT(*) c FROM verdicts GROUP BY reason_code ORDER BY c DESC"
    ).fetchall()
    return [(r["reason_code"], r["c"]) for r in rows]


def antipattern_rate(conn) -> dict:
    total = conn.execute("SELECT COUNT(*) FROM ideas").fetchone()[0]
    hits = conn.execute(
        "SELECT COUNT(DISTINCT idea_id) FROM dupes WHERE method = 'antipattern'"
    ).fetchone()[0]
    by_code: Counter = Counter()
    for row in conn.execute(
        "SELECT detail FROM dupes WHERE method = 'antipattern'"
    ).fetchall():
        by_code[row["detail"].split(":", 1)[0]] += 1
    return {
        "ideas": total,
        "flagged": hits,
        "rate": round(hits / total, 3) if total else None,
        "by_code": by_code.most_common(),
    }


def diversity_by_generator(conn) -> list[dict]:
    out = []
    for gen in ("codex", "tbh"):
        run_ids = [
            r["id"]
            for r in conn.execute(
                "SELECT id FROM runs WHERE generator = ?", (gen,)
            ).fetchall()
        ]
        per_run = [dedup.diversity(conn, rid) for rid in run_ids]
        per_run = [d for d in per_run if d.get("mean_pairwise_distance") is not None]
        if not per_run:
            continue
        worst = max(per_run, key=lambda d: d["max_pairwise_similarity"])
        out.append(
            {
                "generator": gen,
                "runs": len(per_run),
                "mean_within_run_distance": round(
                    sum(d["mean_pairwise_distance"] for d in per_run) / len(per_run), 4
                ),
                "collapse_rate": round(
                    sum(d["collapse_rate"] for d in per_run) / len(per_run), 4
                ),
                "worst_run_max_similarity": worst["max_pairwise_similarity"],
                "closest_pair_titles": worst["closest_pair_titles"],
            }
        )
    return out


# --- judge vs human -------------------------------------------------------


def _kappa(tp: int, fp: int, fn: int, tn: int) -> float | None:
    n = tp + fp + fn + tn
    if n == 0:
        return None
    po = (tp + tn) / n
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / (n * n)
    return None if pe == 1 else round((po - pe) / (1 - pe), 4)


def agreement(conn, threshold: float | None = None, rubric_version: str | None = None) -> dict:
    """Compare the judge's accept/reject call against the human verdict.

    The judge predicts accept when the mean of its rubric dimensions clears `threshold`.
    With no threshold given, sweep and report the operating point with the best macro-F1 —
    the same way the Marketplace quality reviewer is tuned.
    """
    q = (
        "SELECT s.*, v.verdict FROM scores s JOIN verdicts v ON v.idea_id = s.idea_id"
    )
    args: tuple = ()
    if rubric_version:
        q += " WHERE s.rubric_version = ?"
        args = (rubric_version,)
    rows = conn.execute(q, args).fetchall()
    if not rows:
        return {"n": 0, "note": "need both judge scores and human verdicts"}

    def composite(r) -> float | None:
        vals = [r[d] for d in judge.DIMENSIONS if r[d] is not None]
        return sum(vals) / len(vals) if vals else None

    pairs = [
        (composite(r), r["verdict"] == "accept") for r in rows if composite(r) is not None
    ]
    if not pairs:
        return {"n": 0, "note": "scores present but all dimensions null"}

    def at(th: float) -> dict:
        tp = sum(1 for c, h in pairs if c >= th and h)
        fp = sum(1 for c, h in pairs if c >= th and not h)
        fn = sum(1 for c, h in pairs if c < th and h)
        tn = sum(1 for c, h in pairs if c < th and not h)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1_pos = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        nprec = tn / (tn + fn) if tn + fn else 0.0
        nrec = tn / (tn + fp) if tn + fp else 0.0
        f1_neg = 2 * nprec * nrec / (nprec + nrec) if nprec + nrec else 0.0
        return {
            "threshold": round(th, 2),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "f1_accept": round(f1_pos, 3),
            "macro_f1": round((f1_pos + f1_neg) / 2, 3),
            "cohens_kappa": _kappa(tp, fp, fn, tn),
        }

    if threshold is not None:
        best = at(threshold)
        sweep = None
    else:
        lo = min(c for c, _ in pairs)
        hi = max(c for c, _ in pairs)
        steps = [lo + (hi - lo) * i / 20 for i in range(21)] if hi > lo else [lo]
        sweep = [at(t) for t in steps]
        best = max(sweep, key=lambda d: d["macro_f1"])

    return {
        "n": len(pairs),
        "human_accept_rate": round(sum(1 for _, h in pairs if h) / len(pairs), 3),
        "best": best,
        "sweep": sweep,
    }


def downstream(conn) -> dict:
    accepted = conn.execute(
        "SELECT COUNT(*) FROM verdicts WHERE verdict = 'accept'"
    ).fetchone()[0]
    row = conn.execute(
        "SELECT COUNT(*) submitted,"
        " SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END) task_accepted,"
        " AVG(pass_rate) avg_pass_rate, AVG(revisions) avg_revisions"
        " FROM outcomes WHERE submitted_at IS NOT NULL"
    ).fetchone()
    return {
        "ideas_accepted": accepted,
        "submitted": row["submitted"] or 0,
        "task_accepted": row["task_accepted"] or 0,
        "conversion": round((row["submitted"] or 0) / accepted, 3) if accepted else None,
        "avg_pass_rate": round(row["avg_pass_rate"], 3) if row["avg_pass_rate"] else None,
        "avg_revisions": round(row["avg_revisions"], 2) if row["avg_revisions"] else None,
    }


def render(conn) -> str:
    s = summary(conn)
    lines = [
        "",
        "IDEATION CORPUS",
        "═" * 62,
        f"  seeds {s['seeds']}   runs {s['runs']}   ideas {s['ideas']}"
        f"   reviewed {s['reviewed']}   accepted {s['accepted']}",
        "",
        "YIELD BY GENERATOR",
        "─" * 62,
    ]

    yb = yield_by_generator(conn)
    if not yb:
        lines.append("  (no runs yet)")
    for r in yb:
        rate = r["accept_rate"]
        bar = _bar(rate) if rate is not None else "(unreviewed)"
        lines.append(
            f"  {r['generator']:<6} {r['prompt_version']:<6} "
            f"{r['accepted']:>3}/{r['reviewed']:<3} of {r['ideas']:<3} ideas  {bar}"
            + (f"  {rate:.0%}" if rate is not None else "")
        )

    lines += ["", "IDEA COLLAPSE (lower is better — read collapse_rate, not the mean)", "─" * 62]
    dv = diversity_by_generator(conn)
    if not dv:
        lines.append("  (need ≥2 ideas in a run)")
    for d in dv:
        lines.append(
            f"  {d['generator']:<6} collapse {_bar(d['collapse_rate'])} "
            f"{d['collapse_rate']:.0%}   "
            f"mean dist {d['mean_within_run_distance']:.3f}   ({d['runs']} runs)"
        )
        a, b = d["closest_pair_titles"]
        lines.append(
            f"         closest pair ({d['worst_run_max_similarity']:.2f}): "
            f"“{a[:28]}” ↔ “{b[:28]}”"
        )

    ap = antipattern_rate(conn)
    lines += ["", "STALE-PATTERN RATE", "─" * 62]
    if ap["rate"] is None:
        lines.append("  (no ideas yet)")
    else:
        lines.append(f"  {ap['flagged']}/{ap['ideas']} ideas flagged  {_bar(ap['rate'])}  {ap['rate']:.0%}")
        for code, n in ap["by_code"]:
            lines.append(f"      {code:<28} {n}")

    lines += ["", "HUMAN REJECTION REASONS", "─" * 62]
    hist = reason_histogram(conn)
    if not hist:
        lines.append("  (nothing reviewed yet — run `ideation review`)")
    total_reviewed = sum(n for _, n in hist) or 1
    for code, n in hist:
        lines.append(f"  {code:<20} {n:>3}  {_bar(n / total_reviewed)}")

    lines += ["", "JUDGE ↔ HUMAN AGREEMENT", "─" * 62]
    ag = agreement(conn)
    if ag["n"] == 0:
        lines.append(f"  {ag.get('note', 'no data')}")
    else:
        b = ag["best"]
        lines.append(
            f"  n={ag['n']}  human accept rate {ag['human_accept_rate']:.0%}"
        )
        lines.append(
            f"  best operating point: threshold {b['threshold']}  "
            f"macro-F1 {b['macro_f1']}  κ {b['cohens_kappa']}"
        )
        lines.append(
            f"    precision {b['precision']}  recall {b['recall']}  "
            f"(tp {b['tp']} fp {b['fp']} fn {b['fn']} tn {b['tn']})"
        )

    dn = downstream(conn)
    lines += ["", "DOWNSTREAM", "─" * 62]
    lines.append(
        f"  {dn['ideas_accepted']} accepted ideas → {dn['submitted']} submitted"
        f" → {dn['task_accepted']} accepted tasks"
        + (f"   (conversion {dn['conversion']:.0%})" if dn["conversion"] is not None else "")
    )
    lines.append("")
    return "\n".join(lines)


def as_json(conn) -> str:
    return json.dumps(
        {
            "summary": summary(conn),
            "yield_by_generator": yield_by_generator(conn),
            "diversity_by_generator": diversity_by_generator(conn),
            "antipattern_rate": antipattern_rate(conn),
            "reason_histogram": reason_histogram(conn),
            "agreement": agreement(conn),
            "downstream": downstream(conn),
        },
        indent=2,
    )
