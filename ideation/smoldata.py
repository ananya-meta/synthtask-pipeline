"""Smoldata/Codimango validation boundary.

The local harness builds and hardens tasks. Smoldata/Codimango is the external
validation gate: it runs agents, produces pass-rate and review signals, and feeds the
revision loop. The installed CLI exposes inspection/review/rerun commands; task upload
is intentionally represented as an external action that the controller records.
"""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from typing import Any


class SmoldataError(RuntimeError):
    pass


@dataclass(frozen=True)
class CodimangoResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    def json(self) -> Any:
        start = self.stdout.find("{")
        alt = self.stdout.find("[")
        if alt != -1 and (start == -1 or alt < start):
            start = alt
        if start == -1:
            raise SmoldataError("codimango output did not contain JSON")
        return json.loads(self.stdout[start:])


def run_codimango(args: list[str], *, timeout: int = 900) -> CodimangoResult:
    cmd = ["codimango", *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise SmoldataError("codimango CLI is not installed") from exc
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return CodimangoResult(cmd, -1, stdout, stderr or f"timed out after {timeout}s")
    return CodimangoResult(cmd, proc.returncode, proc.stdout, proc.stderr)


def _site_args(site: str) -> list[str]:
    return [] if site == "default" else ["--site", site]


def _status_from_payload(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("status", "state", "validationStatus", "reviewStatus"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value.lower()
        nested = payload.get("task")
        if isinstance(nested, dict):
            return _status_from_payload(nested)
    return "unknown"


def show_task(task_name: str, *, site: str = "default", timeout: int = 900) -> dict:
    result = run_codimango(
        [*_site_args(site), "api", "tasks", "show", task_name, "--json"],
        timeout=timeout,
    )
    if result.returncode != 0:
        raise SmoldataError(result.stderr[-2000:] or result.stdout[-2000:])
    payload = result.json()
    return {"status": _status_from_payload(payload), "payload": payload, "raw": result.stdout}


def watch_task(task_name: str, *, site: str = "default", timeout: int = 3600) -> dict:
    result = run_codimango(
        [*_site_args(site), "api", "tasks", "watch", task_name, "--json"],
        timeout=timeout,
    )
    if result.returncode != 0:
        raise SmoldataError(result.stderr[-2000:] or result.stdout[-2000:])
    payload = result.json()
    return {"status": _status_from_payload(payload), "payload": payload, "raw": result.stdout}


def rerun_task(task_name: str, *, site: str = "default", timeout: int = 900) -> dict:
    result = run_codimango([*_site_args(site), "api", "tasks", "rerun", task_name], timeout=timeout)
    if result.returncode != 0:
        raise SmoldataError(result.stderr[-2000:] or result.stdout[-2000:])
    return {"status": "rerun_requested", "raw": result.stdout}


def agentic_review(
    task_name: str,
    *,
    site: str = "default",
    source_repo: str = "",
    wait: bool = False,
    fail_on_bad: bool = False,
    timeout: int = 3600,
) -> dict:
    args = [*_site_args(site), "api", "jobs", "review", task_name, "--json"]
    if source_repo:
        args += ["--source-repo", source_repo]
    if wait:
        args.append("--wait")
    if fail_on_bad:
        args.append("--fail-on-bad")
    result = run_codimango(args, timeout=timeout)
    if result.returncode not in {0, 1}:
        raise SmoldataError(result.stderr[-2000:] or result.stdout[-2000:])
    try:
        payload = result.json()
    except (json.JSONDecodeError, SmoldataError):
        payload = {"raw": result.stdout}
    verdict = _review_verdict(payload)
    return {
        "status": verdict.lower() if verdict else ("bad" if result.returncode else "good"),
        "verdict": verdict,
        "payload": payload,
        "raw": result.stdout,
        "returncode": result.returncode,
    }


def _review_verdict(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("verdict", "rating", "status", "result"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        review = payload.get("review") or payload.get("agenticReview")
        if isinstance(review, dict):
            return _review_verdict(review)
    return ""


def submission_record(
    task_name: str,
    *,
    status: str,
    platform: str = "smoldata",
    payload: dict | None = None,
    pass_rate: float | None = None,
    revisions: int | None = None,
) -> dict:
    return {
        "platform": platform,
        "external_id": task_name,
        "status": status,
        "pass_rate": pass_rate,
        "revisions": revisions,
        "result": {
            "task_name": task_name,
            "observed_at": time.time(),
            **(payload or {}),
        },
    }
