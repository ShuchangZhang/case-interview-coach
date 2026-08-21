#!/usr/bin/env python3
"""Isolated Git-state tests for the safe skill updater."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import update_skill


def run_git(cwd, *args, check=True):
    return subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=check,
    )


class UpdateSkillGitTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / "origin.git"
        self.publisher = self.root / "publisher"
        self.install = self.root / "install"

        run_git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        run_git(self.root, "clone", str(self.remote), str(self.publisher))
        self._configure(self.publisher)
        self._commit(self.publisher, "version.txt", "one\n", "initial")
        run_git(self.publisher, "push", "-u", "origin", "main")
        run_git(self.root, "clone", str(self.remote), str(self.install))
        self._configure(self.install)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _configure(repository):
        run_git(repository, "config", "user.name", "Updater Test")
        run_git(repository, "config", "user.email", "updater@example.invalid")

    @staticmethod
    def _commit(repository, relative_path, content, message):
        path = repository / relative_path
        path.write_text(content, encoding="utf-8")
        run_git(repository, "add", relative_path)
        run_git(repository, "commit", "-m", message)

    def check(self, **kwargs):
        return update_skill.check_for_updates(
            root=self.install,
            expected_remote=str(self.remote),
            env={},
            **kwargs
        )

    def test_up_to_date_is_silent_continue_state(self):
        result = self.check()
        self.assertEqual(result["status"], "up_to_date")
        self.assertEqual(result["action"], "continue")
        self.assertEqual(result["local_before"], result["remote"])

    def test_remote_ahead_fast_forwards_and_requires_reload(self):
        old_head = run_git(self.install, "rev-parse", "HEAD").stdout.strip()
        self._commit(self.publisher, "version.txt", "two\n", "remote update")
        run_git(self.publisher, "push", "origin", "main")

        result = self.check()

        self.assertEqual(result["status"], "updated")
        self.assertEqual(result["action"], "reload_required")
        self.assertEqual(result["local_before"], old_head)
        self.assertNotEqual(result["local_after"], old_head)
        self.assertEqual((self.install / "version.txt").read_text(encoding="utf-8"), "two\n")

    def test_local_ahead_is_preserved(self):
        self._commit(self.install, "local.txt", "mine\n", "local work")
        local_head = run_git(self.install, "rev-parse", "HEAD").stdout.strip()

        result = self.check()

        self.assertEqual(result["status"], "local_ahead")
        self.assertEqual(run_git(self.install, "rev-parse", "HEAD").stdout.strip(), local_head)
        self.assertTrue((self.install / "local.txt").exists())

    def test_diverged_history_is_preserved(self):
        self._commit(self.install, "local.txt", "mine\n", "local work")
        local_head = run_git(self.install, "rev-parse", "HEAD").stdout.strip()
        self._commit(self.publisher, "remote.txt", "theirs\n", "remote work")
        run_git(self.publisher, "push", "origin", "main")

        result = self.check()

        self.assertEqual(result["status"], "diverged")
        self.assertEqual(run_git(self.install, "rev-parse", "HEAD").stdout.strip(), local_head)
        self.assertFalse((self.install / "remote.txt").exists())

    def test_dirty_tree_is_never_modified(self):
        path = self.install / "version.txt"
        path.write_text("personal edit\n", encoding="utf-8")
        self._commit(self.publisher, "version.txt", "remote edit\n", "remote update")
        run_git(self.publisher, "push", "origin", "main")

        result = self.check()

        self.assertEqual(result["status"], "dirty")
        self.assertEqual(path.read_text(encoding="utf-8"), "personal edit\n")

    def test_untracked_file_also_blocks_update(self):
        untracked = self.install / "notes.txt"
        untracked.write_text("keep me\n", encoding="utf-8")

        result = self.check()

        self.assertEqual(result["status"], "dirty")
        self.assertEqual(untracked.read_text(encoding="utf-8"), "keep me\n")

    def test_wrong_remote_is_rejected_before_fetch(self):
        other = self.root / "other.git"
        run_git(self.root, "init", "--bare", str(other))
        run_git(self.install, "remote", "set-url", "origin", str(other))

        result = self.check()

        self.assertEqual(result["status"], "wrong_remote")

    def test_missing_remote_is_offline_best_effort(self):
        missing = self.root / "missing.git"
        run_git(self.install, "remote", "set-url", "origin", str(missing))

        result = update_skill.check_for_updates(
            root=self.install, expected_remote=str(missing), env={}
        )

        self.assertEqual(result["status"], "offline")
        self.assertEqual(result["action"], "continue")

    def test_fetch_timeout_is_offline_best_effort(self):
        def timeout_fetch(args, cwd, timeout):
            if args and args[0] == "fetch":
                raise subprocess.TimeoutExpired(args, timeout)
            return update_skill._run_git(args, cwd, timeout)

        result = self.check(runner=timeout_fetch)

        self.assertEqual(result["status"], "offline")
        self.assertEqual(result["reason"], "fetch_timeout")

    def test_feature_and_detached_heads_are_not_updated(self):
        run_git(self.install, "checkout", "-b", "feature")
        self.assertEqual(self.check()["status"], "wrong_branch")
        run_git(self.install, "checkout", "main")
        run_git(self.install, "checkout", "--detach")
        result = self.check()
        self.assertEqual(result["status"], "wrong_branch")
        self.assertEqual(result["branch"], "detached")

    def test_update_uses_only_a_fast_forward_write(self):
        self._commit(self.publisher, "version.txt", "two\n", "remote update")
        run_git(self.publisher, "push", "origin", "main")
        commands = []

        def recording_runner(args, cwd, timeout):
            commands.append(tuple(args))
            return update_skill._run_git(args, cwd, timeout)

        result = self.check(runner=recording_runner)

        self.assertEqual(result["status"], "updated")
        flattened = " ".join(" ".join(command) for command in commands)
        for forbidden in ("reset", "stash", "rebase", "checkout"):
            self.assertNotIn(forbidden, flattened)
        self.assertIn(
            ("merge", "--ff-only", "--quiet", "refs/remotes/origin/main"), commands
        )

    def test_post_write_uncertainty_still_requires_reload(self):
        self._commit(self.publisher, "version.txt", "two\n", "remote update")
        run_git(self.publisher, "push", "origin", "main")
        head_reads = {"count": 0}

        def fail_final_verification(args, cwd, timeout):
            if tuple(args) == ("rev-parse", "HEAD"):
                head_reads["count"] += 1
                if head_reads["count"] == 3:
                    return subprocess.CompletedProcess(args, 1, "", "simulated failure")
            return update_skill._run_git(args, cwd, timeout)

        result = self.check(runner=fail_final_verification)

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["action"], "reload_required")
        self.assertEqual((self.install / "version.txt").read_text(encoding="utf-8"), "two\n")


class UpdateSkillPolicyTests(unittest.TestCase):

    def test_only_supported_repository_url_forms_share_an_identity(self):
        expected = "github.com/shuchangzhang/case-interview-coach"
        for remote in (
            "https://github.com/ShuchangZhang/case-interview-coach.git",
            "https://github.com/ShuchangZhang/case-interview-coach",
            "git@github.com:ShuchangZhang/case-interview-coach.git",
            "ssh://git@github.com/ShuchangZhang/case-interview-coach.git",
        ):
            with self.subTest(remote=remote):
                self.assertEqual(update_skill._remote_identity(remote), expected)
        for lookalike in (
            "https://example.com/ShuchangZhang/case-interview-coach.git",
            "https://github.com/another-user/case-interview-coach.git",
            "https://github.com/ShuchangZhang/case-interview-coach-evil.git",
        ):
            with self.subTest(lookalike=lookalike):
                self.assertNotEqual(update_skill._remote_identity(lookalike), expected)

    def test_non_repository_and_disabled_states(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(
                update_skill.check_for_updates(root=root, env={})["status"], "not_git_repo"
            )
            self.assertEqual(
                update_skill.check_for_updates(
                    root=root, env={update_skill.DISABLE_ENV: "1"}
                )["status"],
                "disabled",
            )

    def test_loaded_commit_not_new_disk_commit_is_recorded(self):
        state = {}
        result = {
            "status": "updated",
            "action": "reload_required",
            "local_before": "old-loaded-commit",
            "local_after": "new-disk-commit",
        }

        allowed = update_skill.apply_preflight_result(state, result)

        self.assertFalse(allowed)
        self.assertEqual(state["skill_commit"], "old-loaded-commit")
        self.assertFalse(state["session_start_allowed"])

    def test_preflight_runs_once_per_session_and_again_for_a_fresh_state(self):
        first_session = {}
        self.assertTrue(
            update_skill.should_run_preflight(first_session, "session_initialization")
        )
        update_skill.apply_preflight_result(
            first_session,
            {"status": "offline", "action": "continue", "local_before": "abc"},
        )
        for event in (
            "session_initialization",
            "candidate_turn",
            "between_reps",
            "report_generation",
        ):
            with self.subTest(event=event):
                self.assertFalse(update_skill.should_run_preflight(first_session, event))
        self.assertTrue(update_skill.should_run_preflight({}, "session_initialization"))
        for event in ("candidate_turn", "between_reps", "report_generation"):
            with self.subTest(fresh_state_non_initial_event=event):
                self.assertFalse(update_skill.should_run_preflight({}, event))

    def test_expected_non_update_states_continue_session_start(self):
        for status in (
            "up_to_date",
            "local_ahead",
            "diverged",
            "dirty",
            "offline",
            "not_git_repo",
            "wrong_remote",
            "wrong_branch",
            "disabled",
            "error",
        ):
            with self.subTest(status=status):
                state = {}
                self.assertTrue(
                    update_skill.apply_preflight_result(
                        state, {"status": status, "action": "continue"}
                    )
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
