# Merge protocol

After a sub-agent completes its task and reports back, the primary session merges its branch into `main`. This doc covers how to do that safely.

## The happy path

```bash
# From the main repo's working tree (not a worktree)
cd /path/to/main/repo

# Optional: look at what's coming
git diff --stat main..slice-XX-feature
git log --oneline main..slice-XX-feature

# Merge
git merge --no-ff slice-XX-feature -m "Merge slice-XX-feature: <one-line>"

# Verify
pytest tests/ -q     # or whatever the project's test command is

# Clean up worktree + branch (if the worker pattern used a pre-created worktree)
git worktree remove --force .claude/worktrees/<worktree-name>
git branch -d slice-XX-feature
```

If tests pass, you're done. Move on to the next branch or the next wave.

## Why `--no-ff`

Fast-forward merges silently linearize history. With `--no-ff` each slice gets an explicit merge commit, which means:
- `git log --graph --oneline` shows which merges were which slices.
- Reverting a slice is one `git revert -m 1 <merge-commit>`, not cherry-picking individual commits.
- The task-tracker claim/ship commits stay visible in the dag.

This matters when slices land days apart and you need to trace regressions.

## Merging multiple branches in sequence

When you have several sub-agent branches to merge in the same wave:

```bash
for branch in slice-01-a slice-02-b slice-05-c slice-06-d slice-07-e; do
    echo "=== merging $branch ==="
    git merge --no-ff "$branch" -m "Merge $branch" 2>&1 | tail -4
done
pytest tests/ -q
```

Order doesn't matter when slices are truly disjoint. If tests fail after all merges, bisect: `git bisect` over the merge commits, starting from the last known-good `main`.

## Conflict resolution

### `TASK_TRACKER.md` conflicts

Nearly every wave produces conflicts here because each worker marked `[~]` then `[x]` on their task's line. Two merges at different positions usually apply cleanly; when they don't, it's because two workers edited the SAME slice section (shouldn't happen, but can).

Resolution: open the file, keep BOTH edits (they're independent claims/completions), remove the conflict markers, `git add`, `git merge --continue`.

### Source-file conflicts

These should NOT happen if slicing was correct. If they do:

1. STOP. Don't just resolve by picking one side.
2. Check which slices both touched the file. That's an architecture bug in your slicing.
3. Identify the correct owner; revert the wrong side; re-dispatch the losing task as a follow-up in a next wave.

### Test conflicts

If both branches added tests to the same test file: usually trivially resolvable (different test functions). Keep both.

If both branches added DIFFERENT tests with the SAME name (`test_foo` in both), rename one. Flag this in the next wave's slicing as a naming-convention problem.

### Schema conflicts

If two branches modified `storage.py` schema in incompatible ways: this is the "shared-module violation" case. Revert both schema changes, take the simpler one into `main` as a coordinator patch, then ask both workers to rebase on the new schema.

## Rebase vs. merge

For small, same-wave branches with disjoint files: **merge**. Simpler, explicit, no replay hazards.

For branches that have been stale for days or conflict with other merged work: **rebase the stale branch on fresh main** before merging:

```bash
cd .claude/worktrees/<name>
git fetch <main-repo-path>
git rebase main
# resolve conflicts inside the worktree
git rebase --continue
cd <main-repo>
git merge --no-ff <branch>
```

Never rebase a branch other agents might still be working on.

## When to request changes instead of merge

- Tests fail on the worker's branch. (Their responsibility to fix; re-dispatch to same agent with the failure output.)
- The worker modified files outside their slice's scope. (Handbook violation.)
- Contract changes landed without the "changes requested" note in `TASK_TRACKER.md`. (Same.)
- The structured summary is missing or obviously wrong (e.g. claims a test file they didn't create).
- Scope creep: the branch added unrelated features.

For any of these, don't merge. Tell the user what was wrong and either re-dispatch or take over yourself.

## When to merge-and-fix-forward

- Test failure is trivial (typo, forgotten import) that the primary can fix in under 5 minutes.
- Documentation wording the primary wants to rewrite.
- Small style/formatting issues.

In these cases merge, fix on `main`, amend if needed. Don't bounce the branch back for a 30-second fix.

## Post-merge checklist

After the last branch in a wave merges:

- [ ] `pytest tests/ -q` green on `main`
- [ ] `git worktree list` — no stale worktrees
- [ ] `git branch` — no stale feature branches (they were deleted after merge)
- [ ] `docs/TASK_TRACKER.md` reflects all `[x]` markings from this wave
- [ ] `git log --oneline | head -20` — merge commits are present and readable
- [ ] Summary to user: which branches merged, which tasks now `[x]`, what's unclaimed, suggested next wave

If any of the above fails, don't start the next wave until it's clean.
