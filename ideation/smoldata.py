"""Smoldata/Codimango validation boundary.

The local harness builds and hardens tasks. Smoldata/Codimango is the external
validation gate: it runs agents, produces pass-rate and review signals, and feeds the
revision loop. Task creation happens through the publisher: it commits promoted task
bytes into the GitHub task repo that Codimango ingests, then this module watches and
records the resulting validation/review state.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import secrets
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import publisher


class SmoldataError(RuntimeError):
    pass


DEFAULT_API_URL = "https://smoldata.ai"
DEFAULT_ENV_FILE = Path.home() / ".smoldata-env"


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


# Codimango tags a failing validation detail with a machine-readable `monotoneFailure`
# next to the human prose. Reading the field first means a reworded message can no longer
# silently reclassify a failure.
MONOTONE_FAILURES = {
    "too_easy": "too_easy",
    "too_hard": "too_hard",
    "bad_grading_weak": "bad_grading_weak",
    "weak_grading": "bad_grading_weak",
    "grading_wrong": "grading_wrong",
    "leak": "leak",
    "timeout": "timeout",
    "infra": "infra_error",
    "infra_error": "infra_error",
}

PROSE_FAILURES = (
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

# An unclassifiable failure must not look like a deliberate rejection, otherwise a change
# to Codimango's vocabulary funnels every failure into the same dead end unnoticed.
UNCLASSIFIED_FAILURE = "failed_unclassified"


def _monotone_failure(items: list) -> str:
    for item in items:
        raw = item.get("monotoneFailure")
        if not isinstance(raw, str) or not raw.strip():
            continue
        normalized = raw.strip().lower().replace("-", "_")
        mapped = MONOTONE_FAILURES.get(normalized)
        if mapped:
            return mapped
        # An unrecognised code is still a signal; carry it rather than dropping it.
        return f"{UNCLASSIFIED_FAILURE}:{normalized}"
    return ""


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

    coded = _monotone_failure(failed_details)
    if coded:
        return coded

    text = " ".join(
        " ".join(str(item.get(key, "")) for key in ("label", "status", "detail"))
        for item in failed_details
    ).lower()
    for needle, status in PROSE_FAILURES:
        if needle in text:
            return status
    return UNCLASSIFIED_FAILURE if failed_details else ""


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
    state = _string_value(payload, "state").lower() if isinstance(payload, dict) else ""
    if state in {"in_flight", "not_run", "pending", "running"}:
        status = "pending"
    elif verdict:
        status = verdict.lower()
    else:
        status = "bad" if result.returncode else "good"
    return {
        "status": status,
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


def submit_to_collection(
    source_dir: Path,
    *,
    collection_id: str,
    task_name: str = "",
    api_url: str = "",
    api_key_env: str = "SMOLDATA_API_KEY",
    env_file: Path | None = DEFAULT_ENV_FILE,
    archive_out: Path | None = None,
    timeout: int = 900,
    dry_run: bool = False,
) -> dict[str, Any]:
    package = package_task_archive(
        source_dir,
        task_name=task_name,
        archive_out=archive_out,
    )
    result: dict[str, Any] = {
        "status": "dry_run" if dry_run else "submitted",
        "collection_id": collection_id,
        **package,
    }
    if dry_run:
        result["response"] = None
        return result

    url, api_key = _smoldata_credentials(api_url, api_key_env, env_file)
    response = _post_task_archive(
        url,
        api_key,
        collection_id=collection_id,
        archive_path=Path(package["archive_path"]),
        task_name=package["task_name"],
        idempotency_key=f"{package['task_name']}-{package['archive_sha256']}",
        timeout=timeout,
    )
    result["response"] = response
    return result


def package_task_archive(
    source_dir: Path,
    *,
    task_name: str = "",
    archive_out: Path | None = None,
) -> dict[str, Any]:
    source_dir = source_dir.expanduser().resolve()
    name = task_name or source_dir.name
    if not _valid_task_name(name):
        raise SmoldataError(f"invalid task name for archive: {name!r}")
    if not source_dir.is_dir():
        raise SmoldataError(f"source task directory does not exist: {source_dir}")

    try:
        inventory = publisher.task_inventory(source_dir)
    except publisher.PublishError as exc:
        raise SmoldataError(str(exc)) from exc

    if archive_out is None:
        handle = tempfile.NamedTemporaryFile(
            prefix=f"{name}-",
            suffix=".tar.gz",
            delete=False,
        )
        archive_path = Path(handle.name)
        handle.close()
    else:
        archive_path = archive_out.expanduser().resolve()
        archive_path.parent.mkdir(parents=True, exist_ok=True)

    _write_deterministic_task_tarball(source_dir, name, inventory, archive_path)
    return {
        "task_name": name,
        "source_dir": str(source_dir),
        "archive_path": str(archive_path),
        "archive_sha256": _sha256_file(archive_path),
        "inventory_sha256": publisher.inventory_sha256(inventory),
        "file_count": len(inventory),
    }


def _write_deterministic_task_tarball(
    source_dir: Path,
    task_name: str,
    inventory: dict[str, dict[str, Any]],
    archive_path: Path,
) -> None:
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                root = tarfile.TarInfo(task_name)
                root.type = tarfile.DIRTYPE
                root.mode = 0o755
                root.mtime = 0
                root.uid = root.gid = 0
                root.uname = root.gname = ""
                tar.addfile(root)
                for relative, metadata in sorted(inventory.items()):
                    path = source_dir / relative
                    info = tar.gettarinfo(str(path), arcname=f"{task_name}/{relative}")
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mode = 0o755 if metadata["executable"] else 0o644
                    with path.open("rb") as handle:
                        tar.addfile(info, handle)


def _post_task_archive(
    api_url: str,
    api_key: str,
    *,
    collection_id: str,
    archive_path: Path,
    task_name: str,
    idempotency_key: str,
    timeout: int,
) -> Any:
    body, content_type = _multipart_body(
        fields={"collectionId": collection_id},
        files={
            "task": (
                f"{task_name}.tar.gz",
                "application/gzip",
                archive_path.read_bytes(),
            )
        },
    )
    request = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/v1/tasks",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
            "Idempotency-Key": idempotency_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return _decode_api_body(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SmoldataError(
            f"Smoldata collection upload failed ({exc.code}): {detail[-2000:]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SmoldataError(f"Smoldata collection upload failed: {exc}") from exc


def _multipart_body(
    *,
    fields: dict[str, str],
    files: dict[str, tuple[str, str, bytes]],
) -> tuple[bytes, str]:
    boundary = f"----synthtask-{secrets.token_hex(16)}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    for field, (filename, content_type, payload) in files.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("ascii"),
                (
                    f'Content-Disposition: form-data; name="{field}"; '
                    f'filename="{filename}"\r\n'
                ).encode("ascii"),
                f"Content-Type: {content_type}\r\n\r\n".encode("ascii"),
                payload,
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _smoldata_credentials(
    api_url: str,
    api_key_env: str,
    env_file: Path | None,
) -> tuple[str, str]:
    file_env = _load_env_file(env_file) if env_file else {}
    url = (
        api_url
        or os.environ.get("SMOLDATA_URL", "")
        or file_env.get("SMOLDATA_URL", "")
        or DEFAULT_API_URL
    )
    api_key = os.environ.get(api_key_env, "") or file_env.get(api_key_env, "")
    if not api_key:
        raise SmoldataError(
            f"missing Smoldata API key; set {api_key_env} or add it to {env_file}"
        )
    return url, api_key


def _load_env_file(path: Path) -> dict[str, str]:
    expanded = path.expanduser()
    if not expanded.exists():
        return {}
    values: dict[str, str] = {}
    for raw in expanded.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            values[key] = value
    return values


def _decode_api_body(body: bytes) -> Any:
    text = body.decode("utf-8", errors="replace")
    if not text.strip():
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_task_name(name: str) -> bool:
    return bool(name) and "/" not in name and name not in {".", ".."}
