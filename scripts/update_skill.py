#!/usr/bin/env python3
"""Best-effort, fast-forward-only updater for Case Interview Coach.

The command is intentionally self-contained and standard-library only.  It prints
one JSON object so the host skill can apply a deterministic session-start policy.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional, Sequence
from urllib.parse import unquote, urlparse


EXPECTED_REPOSITORY = "https://github.com/ShuchangZhang/case-interview-coach.git"
TARGET_BRANCH = "main"
DEFAULT_TIMEOUT_SECONDS = 8.0
DISABLE_ENV = "CASE_INTERVIEW_COACH_NO_UPDATE"

Runner = Callable[[Sequence[str], Path, float], subprocess.CompletedProcess]


def _run_git(args: Sequence[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess:
    git_env = os.environ.copy()
    git_env["GIT_TERMINAL_PROMPT"] = "0"
    git_env["GCM_INTERACTIVE"] = "Never"
    return subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
        env=git_env,
    )


def _truthy(value: Optional[str]) -> bool:
    return bool(value) and value.strip().lower() in {"1", "true", "yes", "on"}


def _remote_identity(value: str) -> Optional[str]:
    """Return a conservative repository identity for GitHub URLs or local test paths."""
    raw = value.strip().rstrip("/")
    github_patterns = (
        r"https?://github\.com/([^/]+)/([^/]+)",
        r"git@github\.com:([^/]+)/([^/]+)",
        r"ssh://git@github\.com/([^/]+)/([^/]+)",
    )
    for pattern in github_patterns:
        match = re.fullmatch(pattern, raw, flags=re.IGNORECASE)
        if match:
            owner, repository = match.groups()
            if repository.lower().endswith(".git"):
                repository = repository[:-4]
            return "github.com/{}/{}".format(owner.lower(), repository.lower())

    parsed = urlparse(raw)
    if parsed.scheme == "file":
        return "path:" + str(Path(unquote(parsed.path)).resolve())
    if not parsed.scheme and (raw.startswith(('/', './', '../')) or os.sep in raw):
        return "path:" + str(Path(raw).expanduser().resolve())
    return None


def _result(status: str, action: str = "continue", **fields: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "status": status,
        "action": action,
        "target": "origin/{}".format(TARGET_BRANCH),
    }
    result.update(fields)
    return result


def _output(result: subprocess.CompletedProcess) -> str:
    return (result.stdout or "").strip()


def check_for_updates(
    root: Optional[Path] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    expected_remote: str = EXPECTED_REPOSITORY,
    runner: Runner = _run_git,
    env: Optional[Mapping[str, str]] = None,
) -> Dict[str, Any]:
    """Check ``origin/main`` and fast-forward a safe install when possible.

    ``expected_remote`` and ``runner`` are injectable for isolated tests.  The CLI
    deliberately exposes neither: production always trusts the fixed public repo.
    """
    skill_root = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    skill_root = skill_root.resolve()
    environment = os.environ if env is None else env

    if _truthy(environment.get(DISABLE_ENV)):
        return _result("disabled")
    if not skill_root.is_dir():
        return _result("not_git_repo", reason="skill_root_missing")

    loaded_commit: Optional[str] = None
    try:
        top = runner(["rev-parse", "--show-toplevel"], skill_root, timeout)
        if top.returncode != 0 or Path(_output(top)).resolve() != skill_root:
            return _result("not_git_repo")

        head = runner(["rev-parse", "HEAD"], skill_root, timeout)
        if head.returncode != 0:
            return _result("not_git_repo")
        loaded_commit = _output(head)

        origin = runner(["remote", "get-url", "origin"], skill_root, timeout)
        if origin.returncode != 0:
            return _result("wrong_remote", local_before=loaded_commit, reason="origin_missing")
        actual_remote = _output(origin)
        expected_identity = _remote_identity(expected_remote)
        if expected_identity is None or _remote_identity(actual_remote) != expected_identity:
            return _result("wrong_remote", local_before=loaded_commit)

        branch = runner(["symbolic-ref", "--quiet", "--short", "HEAD"], skill_root, timeout)
        if branch.returncode != 0 or _output(branch) != TARGET_BRANCH:
            return _result(
                "wrong_branch",
                local_before=loaded_commit,
                branch=_output(branch) or "detached",
            )

        status = runner(["status", "--porcelain", "--untracked-files=normal"], skill_root, timeout)
        if status.returncode != 0:
            return _result("error", local_before=loaded_commit, reason="status_failed")
        if _output(status):
            return _result("dirty", local_before=loaded_commit, branch=TARGET_BRANCH)

        try:
            fetched = runner(["fetch", "--quiet", "origin", TARGET_BRANCH], skill_root, timeout)
        except subprocess.TimeoutExpired:
            return _result("offline", local_before=loaded_commit, reason="fetch_timeout")
        if fetched.returncode != 0:
            return _result("offline", local_before=loaded_commit, reason="fetch_failed")

        remote_head = runner(
            ["rev-parse", "refs/remotes/origin/{}".format(TARGET_BRANCH)],
            skill_root,
            timeout,
        )
        base = runner(
            ["merge-base", loaded_commit, "refs/remotes/origin/{}".format(TARGET_BRANCH)],
            skill_root,
            timeout,
        )
        if remote_head.returncode != 0 or base.returncode != 0:
            return _result("error", local_before=loaded_commit, reason="ancestry_check_failed")
        remote_commit = _output(remote_head)
        merge_base = _output(base)

        if loaded_commit == remote_commit:
            return _result(
                "up_to_date",
                local_before=loaded_commit,
                local_after=loaded_commit,
                remote=remote_commit,
                branch=TARGET_BRANCH,
            )
        if remote_commit == merge_base:
            return _result(
                "local_ahead",
                local_before=loaded_commit,
                local_after=loaded_commit,
                remote=remote_commit,
                branch=TARGET_BRANCH,
            )
        if loaded_commit != merge_base:
            return _result(
                "diverged",
                local_before=loaded_commit,
                local_after=loaded_commit,
                remote=remote_commit,
                branch=TARGET_BRANCH,
            )

        # Close the race between the first inspection and the write operation.
        branch_again = runner(
            ["symbolic-ref", "--quiet", "--short", "HEAD"], skill_root, timeout
        )
        status_again = runner(
            ["status", "--porcelain", "--untracked-files=normal"], skill_root, timeout
        )
        head_again = runner(["rev-parse", "HEAD"], skill_root, timeout)
        if (
            branch_again.returncode != 0
            or _output(branch_again) != TARGET_BRANCH
            or status_again.returncode != 0
            or _output(status_again)
            or head_again.returncode != 0
            or _output(head_again) != loaded_commit
        ):
            return _result("dirty", local_before=loaded_commit, reason="state_changed")

        merged = runner(
            ["merge", "--ff-only", "--quiet", "refs/remotes/origin/{}".format(TARGET_BRANCH)],
            skill_root,
            timeout,
        )
        if merged.returncode != 0:
            after_failed_merge = runner(["rev-parse", "HEAD"], skill_root, timeout)
            changed = (
                after_failed_merge.returncode == 0
                and _output(after_failed_merge) != loaded_commit
            )
            return _result(
                "error",
                action="reload_required" if changed else "continue",
                local_before=loaded_commit,
                local_after=_output(after_failed_merge) if changed else loaded_commit,
                reason="fast_forward_failed",
            )
        final_head = runner(["rev-parse", "HEAD"], skill_root, timeout)
        if final_head.returncode != 0 or _output(final_head) != remote_commit:
            return _result(
                "error",
                action="reload_required",
                local_before=loaded_commit,
                local_after=_output(final_head) or None,
                reason="post_update_verification_failed",
            )
        return _result(
            "updated",
            action="reload_required",
            local_before=loaded_commit,
            local_after=remote_commit,
            remote=remote_commit,
            branch=TARGET_BRANCH,
        )
    except subprocess.TimeoutExpired:
        return _result("error", local_before=loaded_commit, reason="local_git_timeout")
    except (FileNotFoundError, OSError, ValueError):
        return _result("error", local_before=loaded_commit, reason="git_unavailable")


def should_run_preflight(session_state: Mapping[str, Any], event: str) -> bool:
    """A fresh training Session checks once; report delivery and later turns do not."""
    return event == "session_initialization" and not bool(
        session_state.get("update_preflight_checked")
    )


def apply_preflight_result(
    session_state: MutableMapping[str, Any], result: Mapping[str, Any]
) -> bool:
    """Record the loaded version and return whether training may start."""
    session_state["update_preflight_checked"] = True
    session_state["update_status"] = result.get("status", "error")
    if result.get("local_before"):
        session_state["skill_commit"] = result["local_before"]
    allowed = result.get("action") != "reload_required"
    session_state["session_start_allowed"] = allowed
    return allowed


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the structured result (currently also the default)",
    )
    args = parser.parse_args(argv)
    del args
    print(json.dumps(check_for_updates(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
