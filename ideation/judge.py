"""Codex-as-judge: rubric scoring, and semantic adjudication of prefilter dupe pairs.

Deliberately *not* the same model that generated the ideas. The track's documented
blind spot is that a model reviewing its own output approves it too easily, so the
judge is pinned to Codex while generation may come from either stack.

The judge's value is only as good as its measured agreement with the human verdicts —
see `report.agreement()`.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from . import db, generate

PROMPTS_DIR = db.REPO_ROOT / "prompts"
RUBRIC_PATH = PROMPTS_DIR / "judge_rubric.md"
DIMENSIONS = ("novelty", "feasibility", "difficulty", "interestingness", "verifiability")

SCORE_SCHEMA = {
    "type": "object",
    "required": ["scores"],
    "properties": {
        "scores": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["idea_id", *DIMENSIONS, "rationale"],
                "properties": {
                    "idea_id": {"type": "integer"},
                    **{d: {"type": "number"} for d in DIMENSIONS},
                    "rationale": {"type": "string"},
                },
            },
        }
    },
}


class JudgeError(RuntimeError):
    pass


def _load_rubric() -> str:
    if not RUBRIC_PATH.exists():
        raise JudgeError(
            f"missing {RUBRIC_PATH}. The rubric is human-authored — see prompts/README.md."
        )
    text = RUBRIC_PATH.read_text(encoding="utf-8")
    if text.strip().startswith("<!-- TODO"):
        raise JudgeError(
            f"{RUBRIC_PATH} is still the empty placeholder. Write the rubric criteria "
            f"before running `ideation judge`."
        )
    return text


def rubric_version() -> str:
    return generate.prompt_hash(_load_rubric())


def _run_codex(prompt: str, schema: dict, timeout: int = 900) -> dict | None:
    with tempfile.TemporaryDirectory(prefix="ideation-judge-") as tmp:
        tmp_path = Path(tmp)
        schema_file = tmp_path / "schema.json"
        out_file = tmp_path / "out.txt"
        schema_file.write_text(json.dumps(schema, indent=2), encoding="utf-8")

        cmd = [
            "codex", "exec",
            "--cd", str(tmp_path),
            "--sandbox", "read-only",
            "--skip-git-repo-check",
            "-o", str(out_file),
            "--output-schema", str(schema_file),
            "--", prompt,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if out_file.exists():
            parsed = generate._extract_json(out_file.read_text(encoding="utf-8"))
            if parsed is not None:
                return parsed
        return generate._extract_json(proc.stdout)


def score_ideas(conn, seed_ref: str | None = None, batch: int = 10, limit: int | None = None) -> dict:
    """Score every unscored idea against the human-authored rubric."""
    rubric = _load_rubric()
    version = rubric_version()

    q = (
        "SELECT i.* FROM ideas i"
        " LEFT JOIN scores s ON s.idea_id = i.id AND s.rubric_version = ?"
        " WHERE s.idea_id IS NULL"
    )
    args: list = [version]
    if seed_ref:
        q += " AND i.seed_id = (SELECT id FROM seeds WHERE slug = ? OR arxiv_id = ?)"
        args += [seed_ref, seed_ref]
    q += " ORDER BY i.id"
    if limit:
        q += f" LIMIT {int(limit)}"

    rows = conn.execute(q, tuple(args)).fetchall()
    if not rows:
        return {"scored": 0, "rubric_version": version}

    scored = 0
    for start in range(0, len(rows), batch):
        chunk = rows[start : start + batch]
        payload = [
            {
                "idea_id": r["id"],
                "title": r["title"],
                "statement": r["statement"],
                "assumption_broken": r["assumption_broken"],
                "difficulty_claim": r["difficulty_claim"],
            }
            for r in chunk
        ]
        prompt = (
            f"{rubric}\n\n"
            "## Ideas to score\n\n"
            "```json\n"
            + json.dumps(payload, indent=2, ensure_ascii=False)
            + "\n```\n\n"
            "Return JSON matching the provided schema: one entry per idea_id above.\n"
        )

        result = _run_codex(prompt, SCORE_SCHEMA)
        if not result or "scores" not in result:
            continue

        valid_ids = {r["id"] for r in chunk}
        for item in result["scores"]:
            if item.get("idea_id") not in valid_ids:
                continue
            db.add_score(
                conn,
                item["idea_id"],
                version,
                "codex",
                **{d: item.get(d) for d in DIMENSIONS},
                rationale=item.get("rationale", ""),
            )
            scored += 1

    return {"scored": scored, "rubric_version": version}


DUPE_SCHEMA = {
    "type": "object",
    "required": ["verdicts"],
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["idea_id", "matched_idea_id", "same_task", "rationale"],
                "properties": {
                    "idea_id": {"type": "integer"},
                    "matched_idea_id": {"type": "integer"},
                    "same_task": {"type": "boolean"},
                    "rationale": {"type": "string"},
                },
            },
        }
    },
}


def adjudicate_dupes(conn, min_similarity: float = 0.40, limit: int = 40) -> dict:
    """Ask Codex whether TF-IDF-flagged pairs are genuinely the same underlying task."""
    pairs = conn.execute(
        "SELECT d.idea_id, d.matched_idea_id, d.similarity FROM dupes d"
        " WHERE d.method = 'tfidf' AND d.similarity >= ?"
        " AND NOT EXISTS (SELECT 1 FROM dupes x WHERE x.idea_id = d.idea_id"
        "   AND x.matched_idea_id = d.matched_idea_id AND x.method = 'codex')"
        " ORDER BY d.similarity DESC LIMIT ?",
        (min_similarity, limit),
    ).fetchall()
    if not pairs:
        return {"adjudicated": 0, "confirmed": 0}

    def brief(idea_id: int) -> dict:
        r = conn.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,)).fetchone()
        return {"idea_id": r["id"], "title": r["title"], "statement": r["statement"]}

    payload = [
        {"a": brief(p["idea_id"]), "b": brief(p["matched_idea_id"]), "lexical_similarity": p["similarity"]}
        for p in pairs
    ]
    prompt = (
        "You are de-duplicating candidate coding-benchmark task ideas.\n\n"
        "Two ideas are the SAME TASK if an agent solving one would produce substantially "
        "the same artifact and exercise the same capability. Surface wording, different "
        "datasets, or a different framing do NOT make them different tasks. Conversely, "
        "shared vocabulary alone does not make them the same.\n\n"
        "For each pair, set same_task true or false and give a one-sentence rationale.\n\n"
        "```json\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n```\n"
    )

    result = _run_codex(prompt, DUPE_SCHEMA)
    if not result or "verdicts" not in result:
        return {"adjudicated": 0, "confirmed": 0}

    confirmed = 0
    for v in result["verdicts"]:
        same = bool(v.get("same_task"))
        db.add_dupe(
            conn,
            v["idea_id"],
            v["matched_idea_id"],
            "codex",
            1.0 if same else 0.0,
            v.get("rationale", ""),
        )
        confirmed += same

    return {"adjudicated": len(result["verdicts"]), "confirmed": confirmed}
