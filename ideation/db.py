"""SQLite store for the synthetic task pipeline corpus.

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

CREATE TABLE IF NOT EXISTS discovery_bundles (
    id           INTEGER PRIMARY KEY,
    seed_id      INTEGER REFERENCES seeds(id),
    bundle_key   TEXT UNIQUE NOT NULL,
    title        TEXT NOT NULL,
    source       TEXT NOT NULL,
    source_url   TEXT,
    path         TEXT,
    payload_json TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'new',
    added_at     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS task_contracts (
    id                 INTEGER PRIMARY KEY,
    idea_id            INTEGER NOT NULL REFERENCES ideas(id),
    discovery_bundle_id INTEGER REFERENCES discovery_bundles(id),
    version            INTEGER NOT NULL DEFAULT 1,
    status             TEXT NOT NULL DEFAULT 'draft',
    objective          TEXT NOT NULL,
    hidden_principle   TEXT NOT NULL,
    allowed_inputs     TEXT NOT NULL,
    forbidden_leaks    TEXT NOT NULL,
    oracle_strategy    TEXT NOT NULL,
    mutation_strategy  TEXT NOT NULL,
    infra_requirements TEXT NOT NULL,
    difficulty_target  TEXT NOT NULL,
    contract_json      TEXT NOT NULL,
    created_at         REAL NOT NULL,
    updated_at         REAL NOT NULL,
    UNIQUE (idea_id, version)
);

CREATE TABLE IF NOT EXISTS scaffold_runs (
    id             INTEGER PRIMARY KEY,
    contract_id    INTEGER NOT NULL REFERENCES task_contracts(id),
    builder        TEXT NOT NULL,
    model          TEXT,
    revision       INTEGER NOT NULL DEFAULT 1,
    workspace_root TEXT NOT NULL,
    canonical_root TEXT,
    state          TEXT NOT NULL DEFAULT 'started',
    started_at     REAL NOT NULL,
    finished_at    REAL,
    exit_code      INTEGER,
    stderr_tail    TEXT
);

CREATE TABLE IF NOT EXISTS verification_runs (
    id              INTEGER PRIMARY KEY,
    scaffold_run_id INTEGER NOT NULL REFERENCES scaffold_runs(id),
    verifier        TEXT NOT NULL,
    command         TEXT NOT NULL,
    status          TEXT NOT NULL,
    stdout_tail     TEXT,
    stderr_tail     TEXT,
    started_at      REAL NOT NULL,
    finished_at     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS review_records (
    id              INTEGER PRIMARY KEY,
    scaffold_run_id INTEGER NOT NULL REFERENCES scaffold_runs(id),
    reviewer        TEXT NOT NULL,
    kind            TEXT NOT NULL,
    verdict         TEXT NOT NULL,
    issues_json     TEXT NOT NULL,
    note            TEXT,
    created_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS submissions (
    id              INTEGER PRIMARY KEY,
    scaffold_run_id INTEGER NOT NULL REFERENCES scaffold_runs(id),
    platform        TEXT NOT NULL,
    external_id     TEXT,
    status          TEXT NOT NULL,
    pass_rate       REAL,
    revisions       INTEGER,
    result_json     TEXT NOT NULL,
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS publish_records (
    id              INTEGER PRIMARY KEY,
    scaffold_run_id INTEGER NOT NULL REFERENCES scaffold_runs(id),
    task_name       TEXT NOT NULL,
    remote_url      TEXT NOT NULL,
    branch          TEXT NOT NULL,
    commit_sha      TEXT,
    github_url      TEXT,
    status          TEXT NOT NULL,
    payload_json    TEXT NOT NULL,
    created_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_events (
    id           INTEGER PRIMARY KEY,
    scope_type   TEXT NOT NULL,
    scope_id     INTEGER NOT NULL,
    label        TEXT NOT NULL,
    detail       TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at   REAL NOT NULL
);

-- Per-contract run settings. Without these the orchestrator only ever learns how to
-- verify and publish a task from CLI flags, so an unattended sweep has nothing to go on.
CREATE TABLE IF NOT EXISTS contract_settings (
    contract_id       INTEGER PRIMARY KEY REFERENCES task_contracts(id),
    verify_commands   TEXT NOT NULL DEFAULT '[]',
    canonical_root    TEXT NOT NULL DEFAULT '',
    publish_task_name TEXT NOT NULL DEFAULT '',
    publish_remote    TEXT NOT NULL DEFAULT '',
    publish_branch    TEXT NOT NULL DEFAULT '',
    publish_method    TEXT NOT NULL DEFAULT '',
    smoldata_site     TEXT NOT NULL DEFAULT '',
    source_repo       TEXT NOT NULL DEFAULT '',
    auto_advance      INTEGER NOT NULL DEFAULT 0,
    created_at        REAL NOT NULL,
    updated_at        REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ideas_seed ON ideas(seed_id);
CREATE INDEX IF NOT EXISTS idx_ideas_run  ON ideas(run_id);
CREATE INDEX IF NOT EXISTS idx_runs_seed  ON runs(seed_id);
CREATE INDEX IF NOT EXISTS idx_contracts_idea ON task_contracts(idea_id);
CREATE INDEX IF NOT EXISTS idx_scaffolds_contract ON scaffold_runs(contract_id);
CREATE INDEX IF NOT EXISTS idx_submissions_scaffold ON submissions(scaffold_run_id);
CREATE INDEX IF NOT EXISTS idx_publish_scaffold ON publish_records(scaffold_run_id);
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


# --- downstream lifecycle -------------------------------------------------


def add_discovery_bundle(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("added_at", time.time())
    kw.setdefault("status", "new")
    existing = conn.execute(
        "SELECT id FROM discovery_bundles WHERE bundle_key = ?",
        (kw["bundle_key"],),
    ).fetchone()
    if existing:
        sets = ", ".join(f"{k} = ?" for k in kw if k != "bundle_key")
        values = [v for k, v in kw.items() if k != "bundle_key"]
        conn.execute(
            f"UPDATE discovery_bundles SET {sets} WHERE bundle_key = ?",
            (*values, kw["bundle_key"]),
        )
        conn.commit()
        return existing["id"]

    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO discovery_bundles ({cols}) VALUES ({marks})",
        tuple(kw.values()),
    )
    conn.commit()
    return cur.lastrowid


def list_discovery_bundles(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM discovery_bundles ORDER BY added_at DESC, id DESC"
    ).fetchall()


def get_idea(conn: sqlite3.Connection, idea_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,)).fetchone()


def verdict_for(conn: sqlite3.Connection, idea_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM verdicts WHERE idea_id = ?", (idea_id,)
    ).fetchone()


def next_contract_version(conn: sqlite3.Connection, idea_id: int) -> int:
    row = conn.execute(
        "SELECT MAX(version) AS v FROM task_contracts WHERE idea_id = ?",
        (idea_id,),
    ).fetchone()
    return int(row["v"] or 0) + 1


def add_task_contract(conn: sqlite3.Connection, **kw: Any) -> int:
    now = time.time()
    kw.setdefault("created_at", now)
    kw.setdefault("updated_at", now)
    kw.setdefault("status", "draft")
    kw.setdefault("version", next_contract_version(conn, int(kw["idea_id"])))
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO task_contracts ({cols}) VALUES ({marks})",
        tuple(kw.values()),
    )
    conn.commit()
    return cur.lastrowid


def update_task_contract_status(conn: sqlite3.Connection, contract_id: int, status: str) -> None:
    conn.execute(
        "UPDATE task_contracts SET status = ?, updated_at = ? WHERE id = ?",
        (status, time.time(), contract_id),
    )
    conn.commit()


def get_task_contract(conn: sqlite3.Connection, contract_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM task_contracts WHERE id = ?", (contract_id,)
    ).fetchone()


def list_task_contracts(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT c.*, i.title AS idea_title FROM task_contracts c"
        " JOIN ideas i ON i.id = c.idea_id"
        " ORDER BY c.updated_at DESC, c.id DESC"
    ).fetchall()


def add_scaffold_run(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("started_at", time.time())
    kw.setdefault("state", "started")
    kw.setdefault("revision", 1)
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO scaffold_runs ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    return cur.lastrowid


def update_scaffold_run(conn: sqlite3.Connection, scaffold_run_id: int, **kw: Any) -> None:
    if not kw:
        return
    sets = ", ".join(f"{k} = ?" for k in kw)
    conn.execute(
        f"UPDATE scaffold_runs SET {sets} WHERE id = ?",
        (*kw.values(), scaffold_run_id),
    )
    conn.commit()


def get_scaffold_run(conn: sqlite3.Connection, scaffold_run_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM scaffold_runs WHERE id = ?", (scaffold_run_id,)
    ).fetchone()


def list_scaffold_runs(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT s.*, c.idea_id, i.title AS idea_title FROM scaffold_runs s"
        " JOIN task_contracts c ON c.id = s.contract_id"
        " JOIN ideas i ON i.id = c.idea_id"
        " ORDER BY s.started_at DESC, s.id DESC"
    ).fetchall()


def add_verification_run(conn: sqlite3.Connection, **kw: Any) -> int:
    now = time.time()
    kw.setdefault("started_at", now)
    kw.setdefault("finished_at", now)
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO verification_runs ({cols}) VALUES ({marks})",
        tuple(kw.values()),
    )
    conn.commit()
    return cur.lastrowid


def add_review_record(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("created_at", time.time())
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO review_records ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    return cur.lastrowid


def add_submission(conn: sqlite3.Connection, **kw: Any) -> int:
    now = time.time()
    kw.setdefault("created_at", now)
    kw.setdefault("updated_at", now)
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO submissions ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    return cur.lastrowid


def add_publish_record(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("created_at", time.time())
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO publish_records ({cols}) VALUES ({marks})",
        tuple(kw.values()),
    )
    conn.commit()
    return cur.lastrowid


def publish_record_for_scaffold(
    conn: sqlite3.Connection, scaffold_run_id: int
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM publish_records WHERE scaffold_run_id = ?"
        " ORDER BY created_at DESC, id DESC LIMIT 1",
        (scaffold_run_id,),
    ).fetchone()


def add_learning_event(conn: sqlite3.Connection, **kw: Any) -> int:
    kw.setdefault("created_at", time.time())
    cols = ", ".join(kw)
    marks = ", ".join("?" for _ in kw)
    cur = conn.execute(
        f"INSERT INTO learning_events ({cols}) VALUES ({marks})", tuple(kw.values())
    )
    conn.commit()
    return cur.lastrowid


# --- contract settings ----------------------------------------------------


CONTRACT_SETTING_FIELDS = (
    "verify_commands",
    "canonical_root",
    "publish_task_name",
    "publish_remote",
    "publish_branch",
    "publish_method",
    "smoldata_site",
    "source_repo",
    "auto_advance",
)


def get_contract_settings(
    conn: sqlite3.Connection, contract_id: int
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM contract_settings WHERE contract_id = ?", (contract_id,)
    ).fetchone()


def set_contract_settings(conn: sqlite3.Connection, contract_id: int, **kw: Any) -> None:
    unknown = set(kw) - set(CONTRACT_SETTING_FIELDS)
    if unknown:
        raise ValueError(f"unknown contract setting(s): {', '.join(sorted(unknown))}")
    now = time.time()
    conn.execute(
        "INSERT INTO contract_settings (contract_id, created_at, updated_at)"
        " VALUES (?, ?, ?) ON CONFLICT(contract_id) DO NOTHING",
        (contract_id, now, now),
    )
    if kw:
        sets = ", ".join(f"{k} = ?" for k in kw)
        conn.execute(
            f"UPDATE contract_settings SET {sets}, updated_at = ? WHERE contract_id = ?",
            (*kw.values(), now, contract_id),
        )
    conn.commit()


def list_contract_settings(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM contract_settings ORDER BY contract_id"
    ).fetchall()
