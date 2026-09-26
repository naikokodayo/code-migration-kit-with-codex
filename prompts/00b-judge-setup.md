# 00b — Judge setup

<!-- Modified for the Codex adaptation; see README.md for provenance. -->

**When:** after the feasibility gate signs off "migrate," before Step 1 — but
when the feasibility report's call #3 found that a portable, validated judge
is missing. A public-surface suite or a suite in a third language is a candidate,
not automatically a validated judge. Reuse it, adapting binary selection,
fixtures, or observation interfaces where needed. Skip this prompt only when
that judge's coverage limits and validation against both the original and
known breakage are already documented; carry that evidence into Step 6.
**Prerequisites:** signed-off feasibility verdict; the call #3 test census
(which tests hit the public surface, which import internals).
**Placeholders:** `[target language]`, `[reviewer model]` (from the Model plan
signed off at the feasibility gate).

> Designed, not yet dogfooded — see RUN-NOTES. Runs 1–3 built their judge inside
> Step 6, which is exactly the late-judge failure this prompt exists to prevent
> (Run 1's referee shipped two comparator bugs before it could be trusted). Treat
> the output as a draft to debug, not a verdict to believe.

---

Use a workflow. The migration has no exit condition until a **judge** exists: a
single harness that evaluates the original code and the port on equal terms, so
"are we done?" has a mechanical answer instead of a feeling. The original code
is the executable spec; the judge is how you query it. Build it now, while the
old code still runs and nothing has been translated to bias you.

The judge must run against **both** implementations through the same external
interface — CLI, HTTP, file I/O, exported API — never through source-language
internals. A test that imports an internal function dies with the old language
and can't see the new code, so it can't judge anything. Three steps:

Audit every executable and helper the harness launches. Record which original
or target binary handles each assertion; a passing assertion that still calls
an original helper is mixed-route evidence, not target-language parity.
Reconcile attempted test recipes with result receipts. A recipe that exits
before writing a receipt is unresolved, never a pass or an environment skip;
retain its raw log and the tested binary's hash.

**1. Categorize.** Take the call #3 census and confirm it against the source.
Keep its counting unit and four mutually exclusive categories: **portable**
(including tests needing an adapter), **internal-bound**, **mixed**, and
**unknown**. Reconcile their counts to the original total and keep a path-backed
ledger. For internal-bound tests, record the guarded behavior so it can become
an external scenario. Split mixed behavior into portable and internal checks
without double-counting the original test unit; resolve unknowns with evidence
or leave them explicitly open at the gate. Document any classification changes.

**2. Rewrite for portability.** Convert the portable tests into assertions that
run against both old and new through the external interface — same inputs, same
expected outputs, diffed mechanically. Where no test exists for a behavior the
old code clearly has, write a real-world scenario instead — a small harness of a
handful of real-world scenarios diffed against the original is enough. Then have two
**adversarial reviewers**, separate contexts and disjoint batches, check that no
rewrite weakened an assertion — a loosened tolerance, a dropped field, an
`assert truthy` where the original checked an exact value. Run them on
[reviewer model], per the Model plan — inheriting the session default is a
deviation; log it. Every weakening they confirm against the original test is a
bug in the rewrite, not the reviewer; fix the harness and resample.

**3. Validate the judge against known answers.** Run the full harness against
the **original** code and report executed, passed, failed, and skipped counts.
Investigate each failure before trusting or changing the judge: it may be a
harness defect, an inherited source failure, or an environment/capability issue.
Keep a baseline-failure/skip ledger with evidence and the affected behavior;
never weaken, delete, or silently skip an assertion to obtain a clean baseline.
Fix confirmed harness defects and re-run. Unresolved failures or coverage gaps
must be presented for a human decision at the gate, not declared validated.

Then run the judge against **deliberately broken** original code in disposable
copies — mutate representative behaviors (flip a comparison, drop an error
path, change an output format). First establish a passing original control for
each mutation, then confirm the corresponding check fails on the mutation; an
unrelated pre-existing failure is not evidence that the mutation was caught.
Report each control, mutation and caught failure. A skipped or undetected
mutation leaves that part of the judge unvalidated.

Stop and show me the harness, all four reconciled category counts, the reviewer
findings, the baseline-failure/skip ledger, and both validation runs — original
controls and every mutation outcome.
Nothing in Step 1 starts until I sign off that the judge is real. This harness
is the artifact Step 6 runs to call the migration done; keep it under version
control and keep it running until the end.
Append one timestamped line for this step to `migration/cost-log.tsv` —
create it with header `step\ttimestamp\twall_clock_min\ttokens\tsubagents\tmodel`
if absent; real values where available, `unknown` where not. Plain
tab-separated values, no `key=` prefixes — a valid row looks exactly like:
`3	2026-06-11T14:02Z	21	2035336	35	unknown`
(your step number and values vary; the format doesn't).
