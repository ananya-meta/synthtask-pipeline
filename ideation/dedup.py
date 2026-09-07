"""Cheap, dependency-free duplicate and stale-pattern detection.

This is a *prefilter*, not the final word. Lexical similarity catches restatements and
the obvious attractors; genuine semantic near-duplicates are escalated to Codex in
judge.py. Doing it in this order keeps the expensive model call off the ~90% of pairs
that plain TF-IDF can already separate.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from . import db

ANTIPATTERNS_PATH = db.REPO_ROOT / "config" / "antipatterns.json"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "this", "to", "was",
    "were", "will", "with", "must", "should", "can", "given", "using", "use", "when",
    "which", "while", "their", "they", "them", "than", "then", "there", "these",
    "task", "agent", "implement", "implementation", "build", "write", "create",
}

TOKEN_RE = re.compile(r"[a-z][a-z0-9_]{2,}")


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def idea_text(row) -> str:
    parts = [row["title"] or "", row["statement"] or "", row["assumption_broken"] or ""]
    return " ".join(parts)


def tfidf_vectors(docs: dict[int, str]) -> dict[int, dict[str, float]]:
    tf: dict[int, Counter] = {k: Counter(tokenize(v)) for k, v in docs.items()}
    n_docs = max(len(docs), 1)
    df: Counter = Counter()
    for counts in tf.values():
        df.update(counts.keys())

    vectors: dict[int, dict[str, float]] = {}
    for doc_id, counts in tf.items():
        total = sum(counts.values()) or 1
        vec = {}
        for term, count in counts.items():
            idf = math.log((n_docs + 1) / (df[term] + 1)) + 1.0
            vec[term] = (count / total) * idf
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        vectors[doc_id] = {t: w / norm for t, w in vec.items()}
    return vectors


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b.get(t, 0.0) for t, w in a.items())


def load_antipatterns() -> list[dict]:
    if not ANTIPATTERNS_PATH.exists():
        return []
    data = json.loads(ANTIPATTERNS_PATH.read_text(encoding="utf-8"))
    return data.get("patterns", [])


def match_antipatterns(text: str, patterns: list[dict]) -> list[tuple[str, str]]:
    """Return [(code, matched_phrase)] for every stale attractor this idea trips."""
    low = text.lower()
    hits = []
    for pat in patterns:
        for phrase in pat.get("any", []):
            if phrase.lower() in low:
                hits.append((pat["code"], phrase))
                break
        else:
            for rx in pat.get("regex", []):
                if re.search(rx, low, re.IGNORECASE):
                    hits.append((pat["code"], rx))
                    break
    return hits


def scan(conn, threshold: float = 0.45, run_id: int | None = None) -> dict:
    """Score every (optionally: every new) idea against the corpus and the pattern list.

    Records findings in the `dupes` table so review.py can surface them inline.
    """
    rows = db.all_ideas(conn)
    if not rows:
        return {"scanned": 0, "dupe_pairs": 0, "antipattern_hits": 0}

    docs = {r["id"]: idea_text(r) for r in rows}
    vectors = tfidf_vectors(docs)
    by_id = {r["id"]: r for r in rows}
    targets = [r for r in rows if run_id is None or r["run_id"] == run_id]

    patterns = load_antipatterns()
    dupe_pairs = 0
    ap_hits = 0

    for row in targets:
        idea_id = row["id"]
        for other_id, other_vec in vectors.items():
            if other_id >= idea_id:
                continue  # compare each pair once, always against the older idea
            sim = cosine(vectors[idea_id], other_vec)
            if sim >= threshold:
                db.add_dupe(
                    conn,
                    idea_id,
                    other_id,
                    "tfidf",
                    round(sim, 4),
                    by_id[other_id]["title"],
                )
                dupe_pairs += 1

        for code, phrase in match_antipatterns(docs[idea_id], patterns):
            db.add_dupe(conn, idea_id, None, "antipattern", 1.0, f"{code}: {phrase}")
            ap_hits += 1

    return {
        "scanned": len(targets),
        "dupe_pairs": dupe_pairs,
        "antipattern_hits": ap_hits,
    }


def diversity(conn, run_id: int | None = None, collapse_at: float = 0.25) -> dict:
    """Within-set diversity.

    Mean pairwise distance is reported but is a poor collapse detector: a handful of
    near-identical ideas barely moves the mean once every unrelated pair is averaged in.
    `collapse_rate` — the fraction of pairs at or above `collapse_at` — is the metric to
    read when asking whether a generator keeps circling the same idea.
    """
    rows = (
        db.ideas_for_run(conn, run_id) if run_id is not None else db.all_ideas(conn)
    )
    if len(rows) < 2:
        return {"n": len(rows), "mean_pairwise_distance": None, "collapse_rate": None}

    docs = {r["id"]: idea_text(r) for r in rows}
    vectors = tfidf_vectors(docs)
    ids = list(vectors)
    by_id = {r["id"]: r for r in rows}

    pairs = [
        (cosine(vectors[ids[i]], vectors[ids[j]]), ids[i], ids[j])
        for i in range(len(ids))
        for j in range(i + 1, len(ids))
    ]
    sims = [p[0] for p in pairs]
    worst = max(pairs, key=lambda p: p[0])

    bigrams, total = set(), 0
    for text in docs.values():
        toks = tokenize(text)
        for k in range(len(toks) - 1):
            bigrams.add((toks[k], toks[k + 1]))
            total += 1

    return {
        "n": len(rows),
        "mean_pairwise_distance": round(1.0 - (sum(sims) / len(sims)), 4),
        "collapse_rate": round(sum(1 for s in sims if s >= collapse_at) / len(sims), 4),
        "collapse_at": collapse_at,
        "distinct_2": round(len(bigrams) / total, 4) if total else None,
        "max_pairwise_similarity": round(worst[0], 4),
        "closest_pair": (worst[1], worst[2]),
        "closest_pair_titles": (by_id[worst[1]]["title"], by_id[worst[2]]["title"]),
    }
