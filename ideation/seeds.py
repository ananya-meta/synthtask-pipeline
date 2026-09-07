"""Seed (research paper) discovery and ingest, backed by `meta search.paper`.

A seed directory is self-contained on purpose: the full paper text lives next to the
generated ideas so a task env can later mount the paper without the instruction ever
linking out to arxiv (per track guidance from Vikas).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import db

SEEDS_DIR = db.REPO_ROOT / "seeds"
META_TIMEOUT = 240


def _meta(*args: str) -> str:
    proc = subprocess.run(
        ["meta", *args], capture_output=True, text=True, timeout=META_TIMEOUT
    )
    if proc.returncode != 0:
        raise RuntimeError(f"meta {' '.join(args)} failed:\n{proc.stderr[-1500:]}")
    return proc.stdout


def slugify(text: str, maxlen: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:maxlen].rstrip("-")


def extract_title(blob: str) -> str:
    """Pull the title out of `meta search.paper load` output.

    That output leads with an indented `key: value` metadata block, then repeats the
    fields inside `content:`. LaTeX line-break artifacts (`\\`) survive the pipeline and
    have to be stripped or they end up in the slug.
    """
    for pattern in (r"^\s*title:\s*(.+)$", r"^\s*Title:\s*(.+)$", r"^#\s+(.+)$"):
        m = re.search(pattern, blob, re.MULTILINE)
        if m:
            return re.sub(r"\s+", " ", m.group(1).replace("\\", " ")).strip(" :")
    return ""


def search(query: str, limit: int = 10, sort_by: str = "relevance") -> list[dict]:
    out = _meta(
        "search.paper",
        "search",
        "--query",
        query,
        "--limit",
        str(limit),
        "--sort-by",
        sort_by,
        "--output",
        "json",
    )
    start = out.find("[")
    if start == -1:
        return []
    return json.loads(out[start:])


def fetch_paper(arxiv_id: str, abstract_only: bool = False) -> str:
    args = ["search.paper", "load", "--arxiv-id", arxiv_id, "--no-truncate"]
    if abstract_only:
        args.append("--abstract-only")
    else:
        args += ["--max-sections", "0"]
    return _meta(*args)


def next_index() -> int:
    existing = [p.name for p in SEEDS_DIR.glob("[0-9][0-9]-*") if p.is_dir()]
    nums = [int(n.split("-", 1)[0]) for n in existing if n[:2].isdigit()]
    return max(nums, default=0) + 1


def add(
    conn,
    arxiv_id: str,
    lane: str = "",
    title: str = "",
    year: int | None = None,
    citations: int | None = None,
    notes: str = "",
) -> tuple[int, Path]:
    """Ingest one paper: write its dir, persist a seeds row, return (seed_id, dir)."""
    existing = conn.execute(
        "SELECT * FROM seeds WHERE arxiv_id = ?", (arxiv_id,)
    ).fetchone()
    if existing:
        return existing["id"], SEEDS_DIR / existing["slug"]

    abstract = fetch_paper(arxiv_id, abstract_only=True).strip()
    if not title:
        title = extract_title(abstract) or arxiv_id

    slug = f"{next_index():02d}-{slugify(title)}"
    seed_dir = SEEDS_DIR / slug
    seed_dir.mkdir(parents=True, exist_ok=True)

    (seed_dir / "abstract.md").write_text(abstract + "\n", encoding="utf-8")
    try:
        (seed_dir / "paper.md").write_text(fetch_paper(arxiv_id) + "\n", encoding="utf-8")
    except Exception as exc:  # full text is best-effort; the abstract is the hard requirement
        (seed_dir / "paper.md").write_text(
            f"(full text unavailable: {exc})\n", encoding="utf-8"
        )

    seed_id = db.add_seed(
        conn,
        arxiv_id=arxiv_id,
        slug=slug,
        title=title,
        abstract=abstract,
        url=f"https://arxiv.org/abs/{arxiv_id}",
        lane=lane,
        year=year,
        citations=citations,
        notes=notes,
    )

    (seed_dir / "meta.json").write_text(
        json.dumps(
            {
                "seed_id": seed_id,
                "arxiv_id": arxiv_id,
                "slug": slug,
                "title": title,
                "lane": lane,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # Filled in by hand — this question is the one Hassan credits for his best tasks.
    assumptions = seed_dir / "ASSUMPTIONS.md"
    if not assumptions.exists():
        assumptions.write_text(
            f"# Load-bearing assumptions — {title}\n\n"
            "> What does this paper take for granted that, if broken, would make a genuinely\n"
            "> hard engineering problem? Reimplementing the paper is a rejected idea\n"
            "> (`PAPER_REIMPL`); breaking one of these is the goal.\n\n"
            "1. \n2. \n3. \n\n"
            "## Real datasets available\n\n"
            "- \n",
            encoding="utf-8",
        )

    return seed_id, seed_dir
