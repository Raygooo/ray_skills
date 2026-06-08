# Anti-collision rules

Parallel agent work only works if no two agents in one wave can corrupt each other. This doc defines "can corrupt each other" precisely.

## The four collision classes

### 1. File collisions

Two agents write to the same file. Classic merge conflict. Worst in CSS and test files where edits cluster near the top.

**Rule:** every file in the repo is owned by exactly one slice. Worker agents only modify files their slice owns. Primary session owns shared/cross-cutting files (see §3).

**How to verify:** scan every `docs/SLICES/NN-*.md` brief. The union of "Files you own" should be disjoint. If a file appears twice, one of the slices is wrong.

### 2. Contract collisions

Two agents both modify the same function's signature, or the same SQL table's columns, in incompatible ways. Merges technically succeed (different lines) but runtime breaks.

**Rule:** contracts listed in the slice brief (function signatures, SQL schemas, CLI flags, HTTP routes) are frozen for workers. Changes route through the primary session.

**How to verify:** a slice brief's "Contracts you MUST honor" list must be kept up to date. If a worker needs to break a contract, the handbook tells them to leave a "contract changes requested" note in `TASK_TRACKER.md` and STOP, not ship.

### 3. Shared-module ownership

Files like `storage.py`, `config.py`, `cli.py`, top-level `pipeline.py` are touched by many slices. They CANNOT be owned by one worker slice without starving the others.

**Rule:** designate these as "shared". Workers read from them freely. Writes happen only via:
- Coordinator changes applied by the primary session between waves, OR
- Additive-only changes that cannot break existing callers (e.g. adding a new CLI subcommand with a new handler function — OK; renaming an existing one — NOT OK).

Document this in `SLICES/00-overview.md` under "Shared-but-rarely-edited modules".

### 4. Dependency collisions

Agent A needs agent B's output, but both are dispatched in the same wave. A finishes first, waits (or fails), B finishes, A's work is now wrong.

**Rule:** sequence dependent tasks across waves. "Wave 1 ships the new schema; Wave 2 is allowed to use the new columns." Never dispatch a dependent task before its prerequisite has merged.

## Anti-collision checklist before each wave

Run through this before sending any `Agent` tool calls:

- [ ] Each slice in this wave has a DIFFERENT owner. No two agents own the same slice.
- [ ] No two agents' owned-file lists overlap.
- [ ] No agent's task requires modifying a shared module. (If one does, either hand it to the primary session, or make it additive-only with an explicit callout in the prompt.)
- [ ] No agent's task depends on another in-flight agent's output in this wave.
- [ ] Every dispatched agent has a specific named task (not "pick any").
- [ ] `main` is clean, tests pass, no uncommitted changes before you start spawning worktrees.

## Failure modes when you skip the checklist

| Skip | Symptom | Recovery |
|---|---|---|
| File ownership not disjoint | Merge conflicts when you merge the second branch | Abandon one branch, re-dispatch sequential |
| Contract frozen not enforced | Tests pass on each branch individually, fail on merged main | Revert the newer change; coordinate-and-redo |
| Shared module edited by worker | Merge OK but runtime breaks (e.g. CLI subcommand renamed) | Revert; re-issue as coordinator-applied patch |
| Dependent in same wave | Second agent blocks or ships broken behaviour | Separate into waves; stop the dependent agent |

## Edge cases

- **`TASK_TRACKER.md`** is written by every worker (to mark `[~]` / `[x]` on their task). This is intended; git handles it fine because each worker edits a different slice's section. Do NOT declare it "shared, don't touch."
- **README.md** updates from multiple slices will conflict. Usually not a real problem — defer README work to the primary session after each wave.
- **`requirements.txt` / package dependencies.** If two slices each add a new library, the merge is clean (different lines). Verify compatibility manually; reject conflicting versions.
- **Test files named `test_<module>.py`** where two slices both touch the same `<module>`: route this through one slice only, or split into `test_<module>_<feature>.py` per slice.

## How many agents per wave?

Not about the number. About what each agent needs and provides.

- If every agent's task is self-contained AND you have merge capacity, 5 is fine.
- If any agent needs verification/debugging you'll do yourself, 2–3 is saner.
- More than ~6 agents in one wave: you lose the ability to review each carefully.

The bottleneck is your merge review time, not compute.
