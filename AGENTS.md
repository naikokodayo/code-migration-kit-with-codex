# Operating manual for Codex sessions in this repository

<!-- Modified from the upstream kit for Codex; see README.md for provenance. -->

You are working inside the Codex Migration Kit, or inside a repository
that has adopted it. Read this before acting on any language-migration request.
These migration gates apply to using the kit, not to maintaining the kit itself.
For kit maintenance, run `python3 scripts/check_kit.py`; preserve upstream
copyright notices and historical receipts.

## What this kit is

A six-step process for migrating a codebase from one language to another:
(1) create the map and the rules, (2) stress-test the rules, (3) translate
everything, (4) compile, (5) run it, (6) match behavior. The README defines
each step. The prompts in `prompts/` run them. Do not improvise a different
process when a prompt exists for the step.

## Standing rules — these override convenience

1. **The rulebook is read-only inside any loop.** Implementers, reviewers, and
   fixers cite it; they never edit it. Rulebook amendments are queued for the
   human and applied between batches. The graded party does not relax its own
   grader.
2. **Queues live on disk.** A unit of work is done when its output file exists
   at the path the naming rules dictate — never when an orchestrator remembers
   it. If you find yourself tracking state in conversation, stop and write a
   manifest instead (`scripts/queue_runner.mjs`).
3. **Sign-off gates end the workflow.** When a prompt says "stop and show me"
   or "no fan-out until I sign off," the phase is over: return the evidence and
   exit. Do not proceed on inferred approval. The human re-invokes the next
   phase; resumability is free because of rule 2.
4. **Reviewers are adversarial, separate, and read-only.** Two reviewers per
   unit, separate contexts, assume the work is wrong, touch nothing. Every
   finding cites a rule or a source line. A third rules on disagreements,
   defaulting to not-confirmed. Fixers apply confirmed findings only.
5. **Separate builds from translation loops.** Follow `templates/rules.README.md`:
   the human installs and adapts `.codex/rules/migration.rules` at the gate,
   restarts Codex, and confirms the project config is trusted. Check the file
   and policy decisions before each batch; file existence alone is not proof
   of runtime enforcement. Codex rules govern execution outside the sandbox;
   they are not a universal command or filesystem security boundary. Never
   bypass a restriction with a wrapper, alternate tool, or permission change.
   Only the human-started build daemon runs expensive builds and tests. If the
   required isolation is unavailable, report that limitation and wait for the
   human's isolation setup or explicit waiver. A cheap in-loop typecheck is a
   human-approved change to both the rulebook and rules at a gate.
6. **Recurring failures move upstream.** Fix one instance, fine. See the same
   failure twice more, stop fixing instances: write up which rule produced it,
   queue the rulebook amendment, and propose regenerating the slice that rule
   touched.
7. **The old code is the spec.** It stays runnable until behavior matching is
   done. When a test fails on the new code, run it on the old code before
   classifying: old-fails-too = inherited, not yours. Never skip, delete, or
   weaken a test to make a queue shrink; slow-but-passing goes in a ledger,
   not a commit.
8. **Unknown is an answer.** When neither the rulebook nor the inventory
   decides a question, translate to the most conservative representation the
   target offers, leave a greppable TODO marker, and keep moving. A searchable
   artifact beats a stalled batch.
9. **Keep evidence compact and tied to the code tested.** For each behavior
   slice, keep one final, fail-closed receipt with the source content hash,
   tested binary hash, command, route, counts, and verdict. Missing runs,
   receipts, or hashes are unresolved, never passes. Retain raw output for
   failures and skips. Intermediate duplicate success logs may live in a
   referenced, fixed Git commit instead of multiplying JSON files in the
   current `migration/` tree; do not discard a required queue, baseline ledger,
   or historical receipt.

## Where things live

| Artifact | Path | Created by |
|---|---|---|
| Rulebook | `migration/RULEBOOK.md` (copy from `templates/`) | Step 1 |
| Dependency map | `migration/depmap/` (edges.tsv, order.txt, cycles.txt) | `scripts/depmap_*` |
| Gap inventory | `migration/inventory.tsv` | Step 1, prompt 02 |
| Work manifest | `migration/manifest.tsv` | Step 1, prompt 01's closing action (`scripts/make_manifest.py`) → Step 3 input |
| Stress-test report | `migration/stress-test/` | Step 2 |
| Translated output | path per the rulebook's naming rules | Step 3 |
| Cost log | `migration/cost-log.tsv` | every prompt, one line per gate |
| Deviation log | `migration/RULEBOOK.md`, Deviation log section | written at gates |

If these paths don't exist yet, the migration hasn't started: run
`prompts/00-feasibility.md` first and stop at its verdict.

## Model guidance

Token spend concentrates in loops; blast radius decides the tier, not task
prestige. Rulebook authorship and amendments: largest available model —
one-time work, and every error replicates into every translated file.
Skeptic reviewers: largest or mid tier, depending on gap complexity.
Complex cross-file or security-sensitive paths need independent high-tier
review. Mechanical, low-risk translation and cleanup can use a lower tier;
keep the two independent reviewers and compiler gates. Fixers: mid tier —
the compiler is the real referee. The model plan is the human's decision, made
at the feasibility gate (prompt 00's Model plan section), and it binds every
post-feasibility prompt — 01 through 06 take the chosen tiers as explicit `[model]`
placeholders. Running subagents on an untriggered default is a process
violation — log it in the deviation log (RULEBOOK.md, Deviation log
section).

## Codex orchestration

When a migration prompt requests a workflow, use Codex subagents if available.
Give each worker a disjoint write scope; do not modify related files
concurrently, and do not fan out unrelated files merely to fill agent slots.
Reviewers read only. Start independent reviewers without inherited conversation
history and give each the source, rulebook, inventory slice, and candidate
output, never the other verdict.
Respect the runtime's concurrency limit; smaller batches preserve the topology.
Use the approved available model and reasoning settings per role. If the client
cannot select them, report the limitation instead of pretending a switch occurred.
If subagents or fresh contexts are unavailable, use separate Codex sessions with
the same disk artifacts; do not label one session's repeated passes independent.
For the blind bakeoff, use a fresh session outside the repository with only the
selected source files and target-language brief; no inherited kit instructions.
Prepare isolation before loop restrictions become active. Archive managed
worktrees with the client's worktree tool when available. Do not run prohibited
Git commands to create or clean up a worktree inside a restricted loop.

Kit paths resolve from this kit's root; `migration/` and source/target paths
resolve from the repository being migrated. Invoke kit scripts by their actual
path while keeping the target repository as the working directory.
