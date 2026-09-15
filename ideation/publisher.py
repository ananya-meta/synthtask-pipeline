"""Publish promoted task artifacts to the GitHub task repository.

Codimango discovers tasks from GitHub task repositories. This module automates the
previously manual step: copy a promoted canonical task into the configured task repo,
commit it, push it, and record the commit the validation system should import.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import db

DEFAULT_BRANCH = "main"
DEFAULT_TASK_REPO = "org-272075201@github.com:codimango/ananyajain-tbench.git"
CONTROL_PARTS = {".factory", ".git"}
CACHE_PARTS = {"__pycache__", ".pytest_cache"}
CACHE_SUFFIXES = {".pyc", ".pyo"}


class PublishError(RuntimeError):
    pass


@dataclass(frozen=True)
class PublishResult:
    task_name: str
    remote_url: str
    branch: str
    commit_sha: str
    github_url: str
    status: str
    pushed: bool
    inventory_sha256: str
    method: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_name": self.task_name,
            "remote_url": self.remote_url,
            "branch": self.branch,
            "commit_sha": self.commit_sha,
            "github_url": self.github_url,
            "status": self.status,
            "pushed": self.pushed,
            "inventory_sha256": self.inventory_sha256,
            "method": self.method,
        }


def default_remote() -> str:
    if os.environ.get("SYNTH_TASK_REMOTE"):
        return os.environ["SYNTH_TASK_REMOTE"]
    sibling = db.REPO_ROOT.parent / "ananyajain-tbench"
    if sibling.exists():
        try:
            return _git(
                ["config", "--local", "--get", "remote.origin.url"],
                cwd=sibling,
            ).strip()
        except PublishError:
            pass
    return DEFAULT_TASK_REPO


def publish_task(
    source_dir: Path,
    *,
    task_name: str,
    remote_url: str | None = None,
    branch: str = DEFAULT_BRANCH,
    message: str = "",
    push: bool = True,
    overwrite: bool = False,
    author_name: str = "ananya-meta",
    author_email: str = "ananyajain@meta.com",
    method: str = "auto",
) -> PublishResult:
    source_dir = source_dir.expanduser().resolve()
    if not source_dir.is_dir():
        raise PublishError(f"source task directory does not exist: {source_dir}")
    if not task_name or "/" in task_name or task_name in {".", ".."}:
        raise PublishError(f"invalid task name: {task_name!r}")
    if not (source_dir / "task.toml").exists():
        raise PublishError(f"source task directory must contain task.toml: {source_dir}")
    if method not in {"auto", "git", "github-api"}:
        raise PublishError("publish method must be auto, git, or github-api")

    remote = remote_url or default_remote()
    if not remote:
        raise PublishError("no publish remote configured")
    source_inventory = task_inventory(source_dir)
    inventory_digest = inventory_sha256(source_inventory)

    if method in {"auto", "git"}:
        try:
            return _publish_task_git(
                source_dir,
                task_name=task_name,
                remote_url=remote,
                branch=branch,
                message=message,
                push=push,
                overwrite=overwrite,
                author_name=author_name,
                author_email=author_email,
                source_inventory=source_inventory,
                inventory_digest=inventory_digest,
            )
        except PublishError:
            if method == "git" or not push or not github_repo_name(remote):
                raise

    return _publish_task_github_api(
        source_dir,
        task_name=task_name,
        remote_url=remote,
        branch=branch,
        message=message,
        overwrite=overwrite,
        source_inventory=source_inventory,
        inventory_digest=inventory_digest,
    )


def _publish_task_git(
    source_dir: Path,
    *,
    task_name: str,
    remote_url: str,
    branch: str,
    message: str,
    push: bool,
    overwrite: bool,
    author_name: str,
    author_email: str,
    source_inventory: dict[str, dict[str, Any]],
    inventory_digest: str,
) -> PublishResult:
    with tempfile.TemporaryDirectory(prefix="synthtask-publish-") as tmp:
        repo = Path(tmp) / "repo"
        _git(["clone", remote_url, str(repo)], cwd=Path(tmp))
        _git(["checkout", branch], cwd=repo)

        dest = repo / task_name
        if dest.exists():
            if not dest.is_dir() or dest.is_symlink():
                raise PublishError(f"task {task_name!r} conflicts with a non-directory")
            if task_inventory(dest) == source_inventory:
                commit_sha = _git(["rev-parse", "HEAD"], cwd=repo).strip()
                return PublishResult(
                    task_name=task_name,
                    remote_url=remote_url,
                    branch=branch,
                    commit_sha=commit_sha,
                    github_url=_github_url(remote_url, branch, commit_sha, task_name),
                    status="no_changes",
                    pushed=False,
                    inventory_sha256=inventory_digest,
                    method="git",
                )
            if not overwrite:
                raise PublishError(
                    f"task {task_name!r} already exists on {branch}; pass --overwrite to replace"
                )
            shutil.rmtree(dest)
        _copy_task(source_dir, dest)
        if task_inventory(dest) != source_inventory:
            raise PublishError("published task inventory differs from the source task")

        _git(["add", task_name], cwd=repo)
        if _git(["status", "--porcelain", "--", task_name], cwd=repo).strip():
            commit_message = message or f"Add synthtask task {task_name}"
            _git(
                [
                    "-c",
                    f"user.name={author_name}",
                    "-c",
                    f"user.email={author_email}",
                    "commit",
                    "-m",
                    commit_message,
                ],
                cwd=repo,
            )
            commit_sha = _git(["rev-parse", "HEAD"], cwd=repo).strip()
            status = "published" if push else "committed"
            if push:
                _git(["push", "origin", f"HEAD:{branch}"], cwd=repo)
        else:
            commit_sha = _git(["rev-parse", "HEAD"], cwd=repo).strip()
            status = "no_changes"

    return PublishResult(
        task_name=task_name,
        remote_url=remote_url,
        branch=branch,
        commit_sha=commit_sha,
        github_url=_github_url(remote_url, branch, commit_sha, task_name),
        status=status,
        pushed=push and status == "published",
        inventory_sha256=inventory_digest,
        method="git",
    )


def _publish_task_github_api(
    source_dir: Path,
    *,
    task_name: str,
    remote_url: str,
    branch: str,
    message: str,
    overwrite: bool,
    source_inventory: dict[str, dict[str, Any]],
    inventory_digest: str,
) -> PublishResult:
    repo_name = github_repo_name(remote_url)
    if not repo_name:
        raise PublishError("GitHub API publish requires a github.com remote")

    head = _gh_api_json(f"repos/{repo_name}/git/ref/heads/{branch}")
    head_sha = str((head.get("object") or {}).get("sha") or "")
    if not head_sha:
        raise PublishError(f"could not resolve {repo_name}@{branch}")
    commit = _gh_api_json(f"repos/{repo_name}/git/commits/{head_sha}")
    base_tree_sha = str((commit.get("tree") or {}).get("sha") or "")
    if not base_tree_sha:
        raise PublishError(f"could not resolve base tree for {repo_name}@{branch}")

    remote_tree = _gh_api_json(
        f"repos/{repo_name}/git/trees/{base_tree_sha}?recursive=1"
    )
    existing: dict[str, dict[str, str]] = {}
    conflict = False
    prefix = f"{task_name}/"
    for item in remote_tree.get("tree") or []:
        path = str(item.get("path") or "")
        if path == task_name and item.get("type") != "tree":
            conflict = True
        if path.startswith(prefix) and item.get("type") == "blob":
            existing[path] = {
                "sha": str(item.get("sha") or ""),
                "mode": str(item.get("mode") or ""),
            }
    if conflict:
        raise PublishError(f"task {task_name!r} conflicts with a non-directory")

    source_entries = {
        f"{task_name}/{relative}": {
            "sha": git_blob_sha(source_dir / relative),
            "mode": "100755" if meta["executable"] else "100644",
        }
        for relative, meta in source_inventory.items()
    }
    if existing == source_entries:
        return PublishResult(
            task_name=task_name,
            remote_url=remote_url,
            branch=branch,
            commit_sha=head_sha,
            github_url=_github_url(remote_url, branch, head_sha, task_name),
            status="no_changes",
            pushed=False,
            inventory_sha256=inventory_digest,
            method="github-api",
        )
    if existing and not overwrite:
        raise PublishError(
            f"task {task_name!r} already exists on {branch}; pass --overwrite to replace"
        )

    tree_entries: list[dict[str, Any]] = [
        {
            "path": path,
            "mode": existing[path]["mode"] or "100644",
            "type": "blob",
            "sha": None,
        }
        for path in sorted(set(existing) - set(source_entries))
    ]
    for relative, meta in source_inventory.items():
        file_path = source_dir / relative
        blob = _gh_api_json(
            f"repos/{repo_name}/git/blobs",
            method="POST",
            payload={
                "content": base64.b64encode(file_path.read_bytes()).decode("ascii"),
                "encoding": "base64",
            },
        )
        tree_entries.append(
            {
                "path": f"{task_name}/{relative}",
                "mode": "100755" if meta["executable"] else "100644",
                "type": "blob",
                "sha": blob["sha"],
            }
        )

    new_tree = _gh_api_json(
        f"repos/{repo_name}/git/trees",
        method="POST",
        payload={"base_tree": base_tree_sha, "tree": tree_entries},
    )
    new_tree_sha = str(new_tree.get("sha") or "")
    if not new_tree_sha or new_tree_sha == base_tree_sha:
        return PublishResult(
            task_name=task_name,
            remote_url=remote_url,
            branch=branch,
            commit_sha=head_sha,
            github_url=_github_url(remote_url, branch, head_sha, task_name),
            status="no_changes",
            pushed=False,
            inventory_sha256=inventory_digest,
            method="github-api",
        )

    commit_message = message or f"Add synthtask task {task_name}"
    new_commit = _gh_api_json(
        f"repos/{repo_name}/git/commits",
        method="POST",
        payload={
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [head_sha],
        },
    )
    commit_sha = str(new_commit.get("sha") or "")
    if not commit_sha:
        raise PublishError("GitHub API did not return a commit SHA")
    _gh_api_json(
        f"repos/{repo_name}/git/refs/heads/{branch}",
        method="PATCH",
        payload={"sha": commit_sha, "force": False},
    )
    return PublishResult(
        task_name=task_name,
        remote_url=remote_url,
        branch=branch,
        commit_sha=commit_sha,
        github_url=_github_url(remote_url, branch, commit_sha, task_name),
        status="published",
        pushed=True,
        inventory_sha256=inventory_digest,
        method="github-api",
    )


def publish_scaffold(
    conn,
    scaffold_run_id: int,
    *,
    task_name: str | None = None,
    remote_url: str | None = None,
    branch: str = DEFAULT_BRANCH,
    message: str = "",
    push: bool = True,
    overwrite: bool = False,
    method: str = "auto",
) -> int:
    scaffold = db.get_scaffold_run(conn, scaffold_run_id)
    if scaffold is None:
        raise PublishError(f"no scaffold run #{scaffold_run_id}")
    if not scaffold["canonical_root"]:
        raise PublishError("scaffold must be promoted before publishing")

    source_dir = Path(scaffold["canonical_root"])
    name = task_name or source_dir.name
    result = publish_task(
        source_dir,
        task_name=name,
        remote_url=remote_url,
        branch=branch,
        message=message,
        push=push,
        overwrite=overwrite,
        method=method,
    )
    record_id = db.add_publish_record(
        conn,
        scaffold_run_id=scaffold_run_id,
        task_name=result.task_name,
        remote_url=result.remote_url,
        branch=result.branch,
        commit_sha=result.commit_sha,
        github_url=result.github_url,
        status=result.status,
        payload_json=json.dumps(result.as_dict(), indent=2, sort_keys=True),
    )
    db.update_scaffold_run(conn, scaffold_run_id, state=result.status)
    return record_id


def _git(args: list[str], *, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=_clean_git_env(),
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise PublishError(f"git {' '.join(args)} failed: {detail[-2000:]}")
    return proc.stdout


def _gh_api_json(
    endpoint: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cmd = ["gh", "api", endpoint]
    if method != "GET":
        cmd += ["--method", method]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8") as handle:
        if payload is not None:
            json.dump(payload, handle, separators=(",", ":"))
            handle.flush()
            cmd += ["--input", handle.name]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=_clean_git_env(),
        )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise PublishError(f"gh api {endpoint} failed: {detail[-2000:]}")
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise PublishError(f"gh api {endpoint} did not return JSON") from exc
    if not isinstance(parsed, dict):
        raise PublishError(f"gh api {endpoint} returned non-object JSON")
    return parsed


def _clean_git_env() -> dict[str, str]:
    env = os.environ.copy()
    count = int(env.get("GIT_CONFIG_COUNT", "0") or "0")
    for i in range(count):
        env.pop(f"GIT_CONFIG_KEY_{i}", None)
        env.pop(f"GIT_CONFIG_VALUE_{i}", None)
    env.pop("GIT_CONFIG_COUNT", None)
    return env


def _copy_task(source_dir: Path, dest: Path) -> None:
    shutil.copytree(source_dir, dest, ignore=_ignore_task_names)


def _ignore_task_names(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in CACHE_PARTS or Path(name).suffix in CACHE_SUFFIXES
    }


def task_inventory(root: Path) -> dict[str, dict[str, Any]]:
    root = root.expanduser().resolve()
    inventory: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in CONTROL_PARTS for part in relative.parts):
            raise PublishError("task contains controller or git metadata paths")
        if any(part in CACHE_PARTS for part in relative.parts):
            continue
        if path.suffix in CACHE_SUFFIXES:
            continue
        metadata = path.lstat()
        rel = relative.as_posix()
        if stat.S_ISLNK(metadata.st_mode):
            raise PublishError(f"task contains a symbolic link: {rel}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise PublishError(f"task contains a special file: {rel}")
        inventory[rel] = {
            "sha256": _sha256_file(path),
            "bytes": metadata.st_size,
            "executable": bool(metadata.st_mode & stat.S_IXUSR),
        }
    if "task.toml" not in inventory:
        raise PublishError(f"source task directory must contain task.toml: {root}")
    return inventory


def inventory_sha256(inventory: dict[str, dict[str, Any]]) -> str:
    encoded = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(payload)}\0".encode("ascii"))
    h.update(payload)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _github_url(remote_url: str, branch: str, commit_sha: str, task_name: str) -> str:
    repo = github_repo_name(remote_url)
    if not repo:
        return ""
    ref = commit_sha or branch
    return f"https://github.com/{repo}/tree/{ref}/{task_name}"


def github_repo_name(remote_url: str) -> str:
    patterns = [
        r"github\.com[:/]([^/\s]+/[^/\s.]+)(?:\.git)?$",
        r"https://github\.com/([^/\s]+/[^/\s.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, remote_url)
        if match:
            return match.group(1)
    return ""
