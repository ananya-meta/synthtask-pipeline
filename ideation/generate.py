"""Run idea generation under strict per-generator filesystem isolation.

Isolation is the whole point of this module. Valentina's Codex-vs-TBH comparison was
invalidated because the two agents could read each other's output, and NG Li saw Muse
write outside its assigned workspace. So each run gets a fresh root containing *only*
the seed materials, and we assert that before and after the run.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from pathlib import Path

from . import db

RUNS_DIR = db.REPO_ROOT / "runs"
PROMPTS_DIR = db.REPO_ROOT / "prompts"
SEEDS_DIR = db.REPO_ROOT / "seeds"

# Only these are allowed into an isolation root before the agent starts.
SEED_FILES = ("abstract.md", "paper.md", "ASSUMPTIONS.md")

IDEA_SCHEMA = {
    "type": "object",
    "required": ["ideas"],
    "properties": {
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["title", "statement", "assumption_broken"],
                "properties": {
                    "title": {"type": "string"},
                    "statement": {"type": "string"},
                    "assumption_broken": {"type": "string"},
                    "difficulty_claim": {"type": "string"},
                    "dataset_ref": {"type": "string"},
                },
            },
        }
    },
}


class GeneratorError(RuntimeError):
    pass


def prompt_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()[:12]


def render_prompt(seed_dir: Path, n_ideas: int, template: Path | None = None) -> str:
    """Substitute seed facts into the human-authored generation prompt."""
    tpl_path = template or (PROMPTS_DIR / "generate_ideas.md")
    if not tpl_path.exists():
        raise GeneratorError(
            f"missing prompt template {tpl_path}. This file is human-authored — see "
            f"prompts/README.md for why."
        )
    tpl = tpl_path.read_text(encoding="utf-8")
    if tpl.strip().startswith("<!-- TODO"):
        raise GeneratorError(
            f"{tpl_path} is still the empty placeholder. Write the generation prompt "
            f"before running `synthtask generate`."
        )

    meta = json.loads((seed_dir / "meta.json").read_text())
    assumptions = ""
    if (seed_dir / "ASSUMPTIONS.md").exists():
        assumptions = (seed_dir / "ASSUMPTIONS.md").read_text(encoding="utf-8")

    return (
        tpl.replace("{{N_IDEAS}}", str(n_ideas))
        .replace("{{SEED_TITLE}}", meta.get("title", ""))
        .replace("{{SEED_SLUG}}", meta.get("slug", ""))
        .replace("{{ASSUMPTIONS}}", assumptions)
        .replace("{{OUTPUT_PATH}}", "ideas.json")
    )


def make_isolation_root(seed_dir: Path, generator: str) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    root = RUNS_DIR / seed_dir.name / generator / ts
    root.mkdir(parents=True, exist_ok=True)
    for name in SEED_FILES:
        src = seed_dir / name
        if src.exists():
            shutil.copy2(src, root / name)
    return root


def assert_isolated(root: Path) -> None:
    """Fail loudly if anything other than seed material leaked into the root."""
    allowed = set(SEED_FILES) | {"PROMPT.md", "ideas.json", "stdout.log", "stderr.log", "last_message.txt"}
    stray = [p.name for p in root.iterdir() if p.name not in allowed]
    if stray:
        raise GeneratorError(f"isolation breach in {root}: unexpected entries {stray}")


def _build_cmd(generator: str, root: Path, model: str | None) -> list[str]:
    if generator == "codex":
        cmd = [
            "codex",
            "exec",
            "--cd",
            str(root),
            "--sandbox",
            "workspace-write",
            "--skip-git-repo-check",
            "-o",
            str(root / "last_message.txt"),
            "--output-schema",
            str(root / ".schema.json"),
        ]
        if model:
            cmd += ["-m", model]
        cmd += ["--", (root / "PROMPT.md").read_text(encoding="utf-8")]
        return cmd

    if generator == "tbh":
        cmd = [
            "muse",
            "exec",
            "--workspace",
            str(root),
            "--prompt-file",
            str(root / "PROMPT.md"),
        ]
        if model:
            cmd += ["--model", model]
        return cmd

    raise GeneratorError(f"unknown generator {generator!r} (expected 'codex' or 'tbh')")


def _parse_ideas(root: Path) -> list[dict]:
    """Prefer the file the agent was told to write; fall back to its final message."""
    candidates = [root / "ideas.json", root / "last_message.txt"]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        blob = _extract_json(text)
        if blob is None:
            continue
        if isinstance(blob, dict) and "ideas" in blob:
            return [i for i in blob["ideas"] if isinstance(i, dict)]
        if isinstance(blob, list):
            return [i for i in blob if isinstance(i, dict)]
    return []


def _extract_json(text: str):
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    return None


def run(
    conn,
    seed_ref: str,
    generator: str,
    n_ideas: int = 8,
    model: str | None = None,
    timeout: int = 1800,
    prompt_version: str = "v1",
) -> tuple[int, int]:
    """Generate ideas for one seed with one generator. Returns (run_id, n_persisted)."""
    seed = db.get_seed(conn, seed_ref)
    if seed is None:
        raise GeneratorError(f"no seed matching {seed_ref!r}")
    seed_dir = SEEDS_DIR / seed["slug"]

    prompt = render_prompt(seed_dir, n_ideas)
    root = make_isolation_root(seed_dir, generator)
    (root / "PROMPT.md").write_text(prompt, encoding="utf-8")
    (root / ".schema.json").write_text(json.dumps(IDEA_SCHEMA, indent=2), encoding="utf-8")
    assert_isolated(root)

    run_id = db.start_run(
        conn,
        seed_id=seed["id"],
        generator=generator,
        model=model or "",
        prompt_path=str(PROMPTS_DIR / "generate_ideas.md"),
        prompt_hash=prompt_hash(prompt),
        prompt_version=prompt_version,
        isolation_root=str(root),
    )

    cmd = _build_cmd(generator, root, model)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=root)
        rc, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        rc, out, err = -1, "", f"timed out after {timeout}s"

    (root / "stdout.log").write_text(out, encoding="utf-8")
    (root / "stderr.log").write_text(err, encoding="utf-8")
    (root / ".schema.json").unlink(missing_ok=True)

    ideas = _parse_ideas(root)
    for obj in ideas:
        db.add_idea(conn, run_id, seed["id"], obj)

    db.finish_run(conn, run_id, rc, len(ideas), err)
    return run_id, len(ideas)
