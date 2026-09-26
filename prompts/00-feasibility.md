# 00 — Feasibility report

<!-- Modified for the Codex adaptation; see README.md for provenance. -->

**When:** before anything else. Produces a report and a verdict; preserves
existing tracked files in the repo under survey, except for the cost-log entry
below. Build artifacts belong in a disposable copy or a declared build directory
that leaves tracked files unchanged. Save the report and evidence outside the
target repo in the user-selected output location, or deliver them in chat.
**Prerequisites:** none. **Placeholders:** `[target language]`, `[kit path]`.

---

Read [kit path]/README.md — it defines the six-step process and the prompts
that run it. Open your report by restating the six steps, one line
each. Beyond that opening index, the README is your rubric, not your evidence:
cite it only to name the step you're applying, never to support a claim about
this repo — and the case-study numbers it mentions are not estimates for this
one. Don't run the other prompts yet.

Then read this codebase and tell me what a migration to [target language]
would look like — a report, not code. Read-only commands (grep, git log, line
counts) are fine; no source edits, test execution, translation, or construction
of a new judge at this stage. One build attempt (plus the typecheck, if it is a
separate command) is allowed: record the command, environment, build location,
and whether it was clean or incremental. If it fails, preserve the failure
evidence and report the timing baseline as unavailable; do not repair and retry
or equate an unavailable baseline with an infeasible migration. Every claim
gets a file path or a count you actually gathered; everything else is labeled
an assumption. Too big to read fully? Sample, and say what you skipped.

Make the census reproducible: pin the surveyed revision, note local changes,
and record counting commands and inclusion/exclusion rules. Distinguish tracked
first-party source from generated, vendored, and compatibility code; use
non-overlapping buckets and state the file/line-count denominator. Name the
test counting unit (for example, test files, declared cases, or scenarios);
static entries and assertion counts are not runtime test totals or pass counts.

Start with the case for leaving: pain instances in this code, not the
language's reputation.

Then make three calls for this repo, each ending in one committed line naming
the files that forced it — a call without file paths is no call:

1. **Structure-preserving or redesign?** Does this architecture translate
   one-to-one into idiomatic [target language], or does the move demand
   restructuring?
2. **What does verification cost?** Time the current build and typecheck as
   the baseline; state the scaling assumption behind your estimate for the
   target. Source build timing is not target compile/typecheck timing: do not
   infer a cheap in-loop target referee from a fast source build. Label target
   cost as an estimate or unknown until measured in a later approved phase.
3. **Do the tests survive?** Classify every counted test unit once as portable
   through the public surface (including those needing an adapter), bound to
   source-language internals, mixed, or unknown. Reconcile the four counts
   exactly to the stated total, with up to three path-backed examples from each
   nonempty category. Record adapter requirements separately from portability.
   Public-surface tests may still require an instrumented UI, TTY, repository
   fixtures, or a test-only protocol; document the interfaces the target must
   reproduce. Inspect the oracle: name behaviors it cannot observe and any
   normalization (for example, ignored color or whitespace). Portability does
   not establish semantic coverage or a validated judge. This is a gate, not an
   observation: the migration has no exit condition without a judge that runs
   against both old and new code through the public surface. If too little survives to be that
   judge, the verdict below must name "build the judge first" as a pre-Step-1
   task — `prompts/00b-judge-setup.md`, run between this gate and Step 1 — and
   sketch the parity scenarios you'd check against the old code, the seed for
   that prompt.

Then instantiate the six steps here: what each concretely means in this repo,
and which of this kit's prompts runs it — blanks filled in with this repo's
paths and units of work. Where a step needs analysis you can't do read-only,
the filled-in prompt is the answer, not a guess. Cost is a visible
multiplication — units of work × per-unit estimate — or the word unknown.

Then two sections the gate decision needs:

**Cost & duration.** A banded, order-of-magnitude token estimate for this
migration, derived from the repo you just surveyed — bands only; a precise
number is forbidden, because precise predictions will be wrong and erode
trust. Show the drivers explicitly: file count × review topology
(implementer, two reviewers, fixer per unit) × referee price. Then per
step, estimated wall-clock and active-attention minutes.

**Model plan.** Recommended model tier per phase for this repo, one line of
reasoning each — a decision I make at this gate, not a default. Tier by
blast radius: rulebook authorship and amendments → largest available model
(one-time work; every error replicates into every translated file); skeptic
reviewers → largest or mid tier, by gap complexity; high-volume translation
implementers → mid or small tier; fixers → mid tier (the compiler is the
real referee). Every post-feasibility prompt (01–06) takes my chosen models
as explicit `[model]` parameters.

End with a verdict: migrate now, later, or don't — "don't" is a valid outcome
of a fully sketched plan — plus the single fact that would change it, one this
repo can't tell you, and how you'd check it in under a day. Close with what
you read and what you ran.
Append one timestamped line for this step to `migration/cost-log.tsv` —
create it with header `step\ttimestamp\twall_clock_min\ttokens\tsubagents\tmodel`
if absent; real values where available, `unknown` where not. Plain
tab-separated values, no `key=` prefixes — a valid row looks exactly like:
`3	2026-06-11T14:02Z	21	2035336	35	unknown`
(your step number and values vary; the format doesn't).
