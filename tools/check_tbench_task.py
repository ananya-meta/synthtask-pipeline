#!/usr/bin/env python3
"""Local pre-publish checks for Terminal-Bench task directories."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


REQUIRED = (
    "README.md",
    "task.toml",
    "instruction.md",
    "environment/Dockerfile",
    "tests/test.sh",
    "tests/verifier.py",
    "tests/score_from_ctrf.py",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_required(root: Path) -> None:
    for relative in REQUIRED:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            fail(f"missing required regular file: {relative}")
    if (root / ".factory").exists() or (root / ".git").exists():
        fail("task contains controller or git metadata")
    if not (root / "solution" / "solve.sh").is_file():
        fail("missing optional-but-required-for-this-pipeline solution/solve.sh")
    mode = (root / "tests" / "test.sh").stat().st_mode
    if not mode & stat.S_IXUSR:
        fail("tests/test.sh is not executable")
    test_sh = (root / "tests" / "test.sh").read_text(errors="replace")
    if "/tests/" not in test_sh:
        fail("tests/test.sh must support the Harbor /tests mount")
    if "/logs/verifier/reward.txt" not in test_sh:
        fail("tests/test.sh must write /logs/verifier/reward.txt")


def check_task_toml(root: Path) -> None:
    with (root / "task.toml").open("rb") as handle:
        data = tomllib.load(handle)
    task_name = str((data.get("task") or {}).get("name") or "")
    track_assignment = str((data.get("task") or {}).get("track_assignment") or "")
    if "/" not in task_name or task_name.endswith("/"):
        fail("[task].name must include an org/name value")
    if track_assignment not in {"t-bench-external-repos", "t-bench-multi-turn"}:
        fail("[task].track_assignment must be a supported T-Bench track")
    reward = str((data.get("metadata") or {}).get("reward_type") or "")
    if reward != "binary":
        fail("[metadata].reward_type must be binary")
    if "http://" in (root / "instruction.md").read_text(errors="replace") or "https://" in (
        root / "instruction.md"
    ).read_text(errors="replace"):
        fail("instruction.md must not contain external links")


def run_test(root: Path) -> int:
    reward = Path("/logs/verifier/reward.txt")
    ctrf = Path("/logs/verifier/ctrf.json")
    ctrf.unlink(missing_ok=True)
    reward.unlink(missing_ok=True)
    proc = subprocess.run(
        ["bash", "tests/test.sh"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=60,
    )
    if not reward.exists():
        fail(
            "tests/test.sh did not write /logs/verifier/reward.txt\n"
            f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
        )
    if not ctrf.exists():
        fail(
            "tests/test.sh did not write /logs/verifier/ctrf.json\n"
            f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
        )
    value = reward.read_text().strip()
    if value not in {"0", "1"}:
        fail(f"reward.txt must contain 0 or 1, got {value!r}")
    try:
        summary = json.loads(ctrf.read_text()).get("results", {}).get("summary", {})
        tests = int(summary.get("tests", 0))
        passed = int(summary.get("passed", 0))
        failed = int(summary.get("failed", 0))
        other = int(summary.get("other", 0))
    except Exception as exc:
        fail(f"ctrf.json is not parseable: {exc}")
    expected = 1 if tests > 0 and passed == tests and failed == 0 and other == 0 else 0
    if int(value) != expected:
        fail("reward.txt does not match ctrf.json summary")
    return int(value)


def score_ctrf(ctrf: Path, reward: Path) -> int:
    value = reward.read_text().strip()
    if value not in {"0", "1"}:
        fail(f"reward.txt must contain 0 or 1, got {value!r}")
    try:
        summary = json.loads(ctrf.read_text()).get("results", {}).get("summary", {})
        tests = int(summary.get("tests", 0))
        passed = int(summary.get("passed", 0))
        failed = int(summary.get("failed", 0))
        other = int(summary.get("other", 0))
    except Exception as exc:
        fail(f"ctrf.json is not parseable: {exc}")
    expected = 1 if tests > 0 and passed == tests and failed == 0 and other == 0 else 0
    if int(value) != expected:
        fail("reward.txt does not match ctrf.json summary")
    return int(value)


def run_mounted_verifier(task_root: Path, workspace: Path, logs: Path) -> int:
    ctrf = logs / "ctrf.json"
    reward = logs / "reward.txt"
    ctrf.unlink(missing_ok=True)
    reward.unlink(missing_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    verifier = task_root / "tests" / "verifier.py"
    scorer = task_root / "tests" / "score_from_ctrf.py"
    proc = subprocess.run(
        [sys.executable, "-I", "-S", str(verifier), "--ctrf", str(ctrf)],
        cwd=workspace,
        text=True,
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        [sys.executable, "-I", "-S", str(scorer), str(ctrf), str(reward)],
        cwd=workspace,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if not reward.exists():
        fail(
            "mounted verifier did not write reward.txt\n"
            f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
        )
    return score_ctrf(ctrf, reward)


def check_environment_context(source: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="synthtask-env-check-") as tmp:
        root = Path(tmp)
        workspace = root / "workspace"
        solution = root / "solution"
        logs = root / "logs"
        shutil.copytree(source / "environment", workspace)
        shutil.copytree(source / "solution", solution)

        before = run_mounted_verifier(source, workspace, logs)
        if before != 0:
            fail("environment build context passes before applying solution")
        subprocess.run(["bash", str(solution / "solve.sh")], cwd=workspace, check=True, timeout=60)
        after = run_mounted_verifier(source, workspace, logs)
        if after != 1:
            fail("environment build context does not pass after applying solution")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir", type=Path)
    args = parser.parse_args(argv)

    source = args.task_dir.expanduser().resolve()
    check_required(source)
    check_task_toml(source)

    with tempfile.TemporaryDirectory(prefix="synthtask-check-") as tmp:
        work = Path(tmp) / source.name
        shutil.copytree(source, work, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        before = run_test(work)
        if before != 0:
            fail("clean task passes before applying solution")
        subprocess.run(["bash", "solution/solve.sh"], cwd=work, check=True, timeout=60)
        after = run_test(work)
        if after != 1:
            fail("task does not pass after applying solution")

    check_environment_context(source)

    print("PASS: task fails before solution and passes after solution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
