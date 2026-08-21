# Update Preflight Policy

This reference defines the lifecycle and safety contract for
`scripts/update_skill.py`. It changes installation maintenance only; it does not change case
methodology, session semantics, scoring or reports.

## 1. Claude Code lifecycle audit

Audited on 2026-08-22 with Claude Code 2.1.228 and the official documentation:

- [Skills](https://code.claude.com/docs/en/slash-commands): skill descriptions are available for
  discovery, while the full `SKILL.md` body enters the conversation when the skill is invoked.
  Once invoked, that rendered body remains in conversation context; it is not transparently
  replaced because files on disk later changed.
- [Hooks](https://code.claude.com/docs/en/hooks): a `SessionStart` hook can return
  `reloadSkills: true` so skills changed by that hook are re-scanned before the first prompt.
  `SessionStart`, however, is a Claude Code session/resume/clear/compact lifecycle event, not the
  boundary of every Case Interview Coach training Session inside one conversation.

A standalone skill also cannot install its own pre-invocation hook merely by being invoked: its
skill-scoped hooks become available only after its current instructions have already loaded.
Consequently, a bundled hook cannot reliably update this standalone install before every first
training invocation.

**Chosen architecture: fallback B.** The loaded skill runs a preflight before each new training
Session. If disk is updated, that invocation stops before training and asks the user to invoke
`/case-interview-coach` again; Claude Code then appends the changed rendered Skill content. A new
Claude Code session is the strict-isolation option because previously invoked instructions remain
in an existing conversation. No code claims same-invocation hot reload.

## 2. When the preflight runs

It runs once before each new Full Case, Focused Drill or Beginner Curriculum, including a later
new Session in the same conversation. It does not run:

- on every turn;
- again during the setup flow that follows a successful/best-effort preflight;
- while a training Session is active;
- during terminal report generation; or
- when the user explicitly asks to skip update checks or network access.

The Session state fields `update_preflight_checked` and `update_status` enforce that boundary.

## 3. Trust boundary

Production execution has no configurable update source. The updater resolves its root from its
own file location and requires all of the following:

1. the resolved skill root is exactly a Git worktree root, not merely inside a parent repository;
2. `origin` identifies `github.com/ShuchangZhang/case-interview-coach` using a supported HTTPS or
   SSH spelling;
3. the current branch is exactly `main` (detached HEAD is rejected);
4. tracked and untracked worktree state is clean; and
5. the remote change is a descendant of local `HEAD`.

The test-only Python API accepts a local expected remote so temporary repositories can exercise
the state machine without contacting GitHub. The CLI does not expose that override.

## 4. Safe Git algorithm

The updater uses this sequence, with an eight-second timeout per command:

1. inspect repository root, `HEAD`, `origin`, branch and porcelain status;
2. `git fetch --quiet origin main`;
3. compare `HEAD`, `origin/main` and `git merge-base`;
4. if and only if remote is strictly ahead, re-check branch, cleanliness and unchanged `HEAD`;
5. `git merge --ff-only --quiet refs/remotes/origin/main`;
6. verify final `HEAD` equals the fetched remote commit.

This is the explicit fetch-plus-fast-forward equivalent of `git pull --ff-only origin main`, but
it permits classification before the one write operation and avoids a second network request.

The updater never invokes `reset`, `stash`, `rebase`, checkout, force push, branch deletion,
conflict resolution or a non-fast-forward merge. It never edits user files directly.

## 5. Structured result states

The command prints one JSON object. `action` is normally `continue`. It is `reload_required`
after a successful update and in the defensive case where a write was attempted and disk may have
changed but post-write verification could not establish a clean result.

| `status` | Meaning | Disk action | Session action |
|---|---|---|---|
| `up_to_date` | `HEAD == origin/main` | none | continue silently |
| `updated` | clean `main`, remote strictly ahead, verified fast-forward | fast-forward only | stop and re-invoke |
| `local_ahead` | remote is an ancestor of local | none | explain; continue locally |
| `diverged` | neither side is the other’s ancestor | none | explain; continue locally |
| `dirty` | tracked/untracked changes exist, or state changed during the check | none | explain; continue locally |
| `offline` | fetch failed or timed out | none | brief notice; continue locally |
| `wrong_remote` | origin missing or not the expected repository | none | explain; continue locally |
| `not_git_repo` | install is not the exact Git worktree root | none | explain; continue locally |
| `wrong_branch` | feature branch or detached HEAD | none | explain; continue locally |
| `disabled` | environment opt-out is active | none | continue silently |
| `error` | a local inspection, ancestry or verification step failed | no further action | continue if `action=continue`; stop and reload if post-write uncertainty returned `reload_required` |

Malformed/no output is treated like `error`, never as permission to mutate files and never as a
reason to block training.

## 6. Loaded-version semantics

`local_before` is the commit whose Skill instructions were loaded for the current invocation.
When training continues, it may be stored as `skill_commit`. After `updated`, `local_after` exists
on disk but must not be represented as loaded by the current invocation; training is blocked until
re-invocation. Report rendering is deliberately unchanged in this iteration, so the version stays
in internal Session state rather than becoming new report content.

## 7. User controls and manual diagnostics

- One request: say “do not check for updates” / “不要联网更新”; the skill skips that Session's
  preflight.
- Persistent environment opt-out: set `CASE_INTERVIEW_COACH_NO_UPDATE=1`.
- Manual check/update: from the cloned repository, run
  `python3 scripts/update_skill.py --json`.

Automatic updating is supported only for a Git clone on clean `main` with the expected origin.
Copied folders, archives, forks, dirty worktrees, local branches and divergent histories keep
working from local files but are never rewritten automatically.
