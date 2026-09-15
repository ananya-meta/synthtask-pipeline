"""Smoldata/Codimango validation boundary.

The local harness builds and hardens tasks. Smoldata/Codimango is the external
validation gate: it runs agents, produces pass-rate and review signals, and feeds the
revision loop. Task creation happens through the publisher: it commits promoted task
bytes into the GitHub task repo that Codimango ingests, then this module watches and
records the resulting validation/review state.
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
        nested = payload.get("task")
        if isinstance(nested, dict):
            nested_status = _status_from_payload(nested)
            if nested_status != "unknown":
                return nested_status

        validation_status = _string_value(payload, "validationStatus")
        if validation_status:
            normalized = validation_status.lower()
            if normalized == "failed":
                return _failure_status_from_details(payload) or "rejected"
            if normalized in {"pending", "running"}:
                return "pending"
            if normalized in {"passed", "success", "succeeded"}:
                task_status = _string_value(payload, "status")
                if task_status and task_status.lower() in {"accepted", "needs_revision"}:
                    return task_status.lower()
                return "passed"

        for key in ("status", "state", "reviewStatus"):
            value = _string_value(payload, key)
            if value:
                return value.lower()
    return "unknown"


def _string_value(payload: dict, key: str) -> str:
    value = payload.get(key)
    return value.strip() if isinstance(value, str) else ""


def _failure_status_from_details(payload: dict) -> str:
    details = payload.get("validationDetails")
    if not isinstance(details, list):
        return ""
    failed_details = [
        item
        for item in details
        if isinstance(item, dict)
        and str(item.get("status", "")).lower() in {"failed", "fail"}
    ]
    if not failed_details:
        failed_details = [item for item in details if isinstance(item, dict)]
    text = " ".join(
        " ".join(str(item.get(key, "")) for key in ("label", "status", "detail"))
        for item in failed_details
    ).lower()
    patterns = (
        ("too easy", "too_easy"),
        ("bad_grading_weak", "bad_grading_weak"),
        ("bad grading weak", "bad_grading_weak"),
        ("weak grading", "bad_grading_weak"),
        ("grading wrong", "grading_wrong"),
        ("too hard", "too_hard"),
        ("leak", "leak"),
        ("timeout", "timeout"),
        ("infra", "infra_error"),
    )
    for needle, status in patterns:
        if needle in text:
            return status
    return ""


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
