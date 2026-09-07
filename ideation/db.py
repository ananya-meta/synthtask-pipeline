"""SQLite store for the ideation corpus.

Every idea ever generated is kept, including rejected ones — the rejections carry the
reason codes that train the judge, so they are the point rather than a byproduct.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "data" / "ideation.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS seeds (
    id          INTEGER PRIMARY KEY,
    arxiv_id    TEXT UNIQUE,
    slug        TEXT UNIQUE NOT NULL,
    title       TEXT NOT NULL,
    abstract    TEXT,
    url         TEXT,
    lane        TEXT,
    year        INTEGER,
    citations   INTEGER,
    notes       TEXT,
    added_at    REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS runs (
    id             INTEGER PRIMARY KEY,
    seed_id        INTEGER NOT NULL REFERENCES seeds(id),
    generator      TEXT NOT NULL,          -- 'codex' | 'tbh'
    model          TEXT,
    prompt_path    TEXT,
    prompt_hash    TEXT,
    prompt_version TEXT,
    isolation_root TEXT NOT NULL,
    started_at     REAL NOT NULL,
    finished_at    REAL,
    exit_code      INTEGER,
    n_ideas        INTEGER DEFAULT 0,
    stderr_tail    TEXT
);

CREATE TABLE IF NOT EXISTS ideas (
    id                INTEGER PRIMARY KEY,
    run_id            INTEGER NOT NULL REFERENCES runs(id),
    seed_id           INTEGER NOT NULL REFERENCES seeds(id),
    title             TEXT NOT NULL,
    statement         TEXT NOT NULL,
    assumption_broken TEXT,
    difficulty_claim  TEXT,
    dataset_ref       TEXT,
    raw_json          TEXT,
    created_at        REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS scores (
    idea_id         INTEGER NOT NULL REFERENCES ideas(id),
    rubric_version  TEXT NOT NULL,
    judge           TEXT NOT NULL,
    novelty         REAL,
    feasibility     REAL,
    difficulty      REAL,
    interestingness REAL,
    verifiability   REAL,
    rationale       TEXT,
    created_at      REAL NOT NULL,
    PRIMARY KEY (idea_id, rubric_version, judge)
);

CREATE TABLE IF NOT EXISTS dupes (
    idea_id         INTEGER NOT NULL REFERENCES ideas(id),
    matched_idea_id INTEGER REFERENCES ideas(id),
    method          TEXT NOT NULL,         -- 'tfidf' | 'antipattern' | 'codex'
    similarity      REAL,
    detail          TEXT,
    PRIMARY KEY (idea_id, matched_idea_id, method)
);

CREATE TABLE IF NOT EXISTS verdicts (
    idea_id     INTEGER PRIMARY KEY REFERENCES ideas(id),
    verdict     TEXT NOT NULL,             -- 'accept' | 'reject'
    reason_code TEXT NOT NULL,
    note        TEXT,
    reviewed_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS outcomes (
    idea_id          INTEGER PRIMARY KEY REFERENCES ideas(id),
    scaffolded       INTEGER DEFAULT 0,
    submitted_at     REAL,
    smoldata_task_id TEXT,
    accepted         INTEGER,
    pass_rate        REAL,
    revisions        INTEGER,
    note             TEXT
);

CREATE INDEX IF NOT EXISTS idx_ideas_seed ON ideas(seed_id);
CREATE INDEX IF NOT EXISTS idx_ideas_run  ON ideas(run_id);
CREATE INDEX IF NOT EXISTS idx_runs_seed  ON runs(seed_id);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


# --- seeds ----------------------------------------------------------------


def add_seed(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("added_at", time.time())
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT OR IGNORE INTO seeds ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    if cur.lastrowid:
        return cur.lastrowid
    row = conn.execute(
        "SELECT id FROM seeds WHERE slug = ?", (kw["slug"],)
    ).fetchone()
    return row["id"]


def get_seed(conn: sqlite3.Connection, ref: str) -> sqlite3.Row | None:
    """Look a seed up by slug, arxiv id, or numeric id."""
    return conn.execute(
        "SELECT * FROM seeds WHERE slug = ? OR arxiv_id = ? OR id = ?",
        (ref, ref, ref if str(ref).isdigit() else -1),
    ).fetchone()


def list_seeds(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM seeds ORDER BY id").fetchall()


# --- runs -----------------------------------------------------------------


def start_run(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("started_at", time.time())
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO runs ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    return cur.lastrowid


def finish_run(
    conn: sqlite3.Connection,
    run_id: int,
    exit_code: int,
    n_ideas: int,
    stderr_tail: str = "",
) -> None:
    conn.execute(
        "UPDATE runs SET finished_at = ?, exit_code = ?, n_ideas = ?, stderr_tail = ?"
        " WHERE id = ?",
        (time.time(), exit_code, n_ideas, stderr_tail[-2000:], run_id),
    )
    conn.commit()


# --- ideas ----------------------------------------------------------------


def add_idea(conn: sqlite3.Connection, run_id: int, seed_id: int, obj: dict) -> int:
    cur = conn.execute(
        "INSERT INTO ideas (run_id, seed_id, title, statement, assumption_broken,"
        " difficulty_claim, dataset_ref, raw_json, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            run_id,
            seed_id,
            obj.get("title", "").strip(),
            obj.get("statement", "").strip(),
            obj.get("assumption_broken"),
            obj.get("difficulty_claim"),
            obj.get("dataset_ref"),
            json.dumps(obj, ensure_ascii=False),
            time.time(),
        ),
    )
    conn.commit()
    return cur.lastrowid


def all_ideas(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM ideas ORDER BY id").fetchall()


def ideas_for_run(conn: sqlite3.Connection, run_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM ideas WHERE run_id = ? ORDER BY id", (run_id,)
    ).fetchall()


def unreviewed_ideas(conn: sqlite3.Connection, seed_ref: str | None = None) -> list[sqlite3.Row]:
    q = (
        "SELECT i.* FROM ideas i"
        " LEFT JOIN verdicts v ON v.idea_id = i.id"
        " WHERE v.idea_id IS NULL"
    )
    args: tuple = ()
    if seed_ref:
        q += " AND i.seed_id = (SELECT id FROM seeds WHERE slug = ? OR arxiv_id = ?)"
        args = (seed_ref, seed_ref)
    return conn.execute(q + " ORDER BY i.id", args).fetchall()


# --- dupes / scores / verdicts / outcomes ---------------------------------


def add_dupe(
    conn: sqlite3.Connection,
    idea_id: int,
    matched_idea_id: int | None,
    method: str,
    similarity: float,
    detail: str = "",
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO dupes (idea_id, matched_idea_id, method, similarity, detail)"
        " VALUES (?, ?, ?, ?, ?)",
        (idea_id, matched_idea_id, method, similarity, detail),
    )
    conn.commit()


def dupes_for(conn: sqlite3.Connection, idea_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM dupes WHERE idea_id = ? ORDER BY similarity DESC", (idea_id,)
    ).fetchall()


def add_score(conn: sqlite3.Connection, idea_id: int, rubric_version: str, judge: str, **dims: Any) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO scores (idea_id, rubric_version, judge, novelty,"
        " feasibility, difficulty, interestingness, verifiability, rationale, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            idea_id,
            rubric_version,
            judge,
            dims.get("novelty"),
            dims.get("feasibility"),
            dims.get("difficulty"),
            dims.get("interestingness"),
            dims.get("verifiability"),
            dims.get("rationale"),
            time.time(),
        ),
    )
    conn.commit()


def score_for(conn: sqlite3.Connection, idea_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM scores WHERE idea_id = ? ORDER BY created_at DESC LIMIT 1",
        (idea_id,),
    ).fetchone()


def add_verdict(
    conn: sqlite3.Connection, idea_id: int, verdict: str, reason_code: str, note: str = ""
) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO verdicts (idea_id, verdict, reason_code, note, reviewed_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (idea_id, verdict, reason_code, note, time.time()),
    )
    conn.commit()


def set_outcome(conn: sqlite3.Connection, idea_id: int, **kw: Any) -> None:
    existing = conn.execute(
        "SELECT idea_id FROM outcomes WHERE idea_id = ?", (idea_id,)
    ).fetchone()
    if existing:
        sets = ", ".join(f"{k} = ?" for k in kw)
        conn.execute(
            f"UPDATE outcomes SET {sets} WHERE idea_id = ?",
            (*kw.values(), idea_id),
        )
    else:
        kw["idea_id"] = idea_id
        cols = ", ".join(kw)
        marks = ", ".join("?" for _ in kw)
        conn.execute(f"INSERT INTO outcomes ({cols}) VALUES ({marks})", tuple(kw.values()))
    conn.commit()


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]
