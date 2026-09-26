# 04 — Translation kickoff

<!-- Modified for the Codex adaptation; see README.md for provenance. -->

**When:** Step 3, after the stress test is signed off. **Prerequisites:**
amended RULEBOOK.md, complete inventory, manifest at `migration/manifest.tsv`
(source path → target path per the rulebook's naming rules), and
`templates/migration.rules` copied to the target repo's `.codex/rules/migration.rules`
with setup verified per `templates/rules.README.md`.
**Placeholders:** `[100]` (batch size), `[TODO(port)]` (your
greppable markers — TODO/PERF/BUG per rulebook §3), `[implementer model]`,
`[reviewer model]` (from the Model plan signed off at the feasibility gate).
Swap "file" for whatever your queue emits — modules, units.

This prompt is deliberately short. By Step 3 the rulebook is the prompt — if
your kickoff needs to be longer than this, your rulebook isn't done.

---

Before every fan-out, including re-rounds, verify the human-installed
`.codex/rules/migration.rules` using `templates/rules.README.md`: inspect the
adapted prefixes, check decisions with `codex execpolicy check`, and confirm
the human restarted Codex with the project config trusted. File existence or
an offline rule check alone does not prove runtime enforcement. Codex rules
cover execution outside the sandbox, not every tool or command path. Keep
builds/tests in the separate human-run daemon; never route around restrictions.
If setup or required isolation is missing, stop and report the exact missing
piece, or record an explicit human waiver at the gate. Never install, overwrite,
or relax active rules from inside the loop.

Set the model explicitly on every agent call: implementers on
[implementer model], reviewers on [reviewer model]; fixers ride
[implementer model] unless the Model plan says otherwise. Inheriting the
session default is a deviation; log it. Use the approved lower tier for
mechanical, low-risk slices; send cross-file or security-sensitive slices to
independent high-tier review. Assign disjoint write scopes and keep coupled
files in one coordinated slice rather than editing them concurrently.

Use a workflow. The queue is every `migration/manifest.tsv` entry with no
translated file on disk yet — so reruns resume for free. Work down it in
batches of [100]. Every
agent reads the **rulebook**; each implementer translates its one file —
[TODO(port)] anything the rulebook doesn't decide, status trailer at the
bottom. Two adversarial **reviewers** per file, separate contexts, assume it's
wrong, touch nothing — every finding cites a rule or a source line; a third
rules on anything they don't agree on, defaulting to not-confirmed. **Fix
agents** apply confirmed findings only — can't fix it, flag it. Don't run the
compiler — it grades everything next step (exception: if Step 4 has dissolved
into this loop per README Step 4, the rulebook's §0 names the cheap in-loop
referee). Four agents per file is the multiplier and the product: Run 1's
catches came from adversarial review at the map, inventory, and bakeoff
stages — and the one run that skipped this per-file pass ate the exact
failure class it exists to catch in the compile step (RUN-NOTES, Run 1
deviations).

For commands that modify external state, reviewers must trace selection context
from the active view through argument expansion to the actual write target.
A shell-free API or memory-safe language does not prove that the correct branch,
remote, file, or account is selected. Reject unavailable context rather than
substituting a convenient default. At the permitted validation stage, exercise
two distinguishable targets and verify that the unselected one is unchanged.
For patch-based writes, compare the displayed path with the path the apply
command resolves *after* prefix stripping. Check every patch section before
slicing out a selected hunk or line; an unsupported earlier section must not
turn a later file into the selected target. Test configured prefixes and two
same-named files at different depths, and verify the index remains unchanged
when an unsafe patch is rejected.
For interactive commands, separately verify the controlling terminal,
confirmation text, visible results, and terminal restoration after failure.

Progress invariant: translated-file count on disk must grow between polls.
No growth from a worker for three minutes means treat it as failed — recover
its output from the journal or disk, and report the stall. Stalls are yours
to heal, not mine to notice. At each batch gate, report burndown plus an
estimated duration for the next step (survey build — or Steps 5–6 if Step 4
dissolved) — wall-clock and active-attention minutes, from the batch timings
you just measured.
Append one timestamped line for this step to `migration/cost-log.tsv` —
create it with header `step\ttimestamp\twall_clock_min\ttokens\tsubagents\tmodel`
if absent; real values where available, `unknown` where not. Plain
tab-separated values, no `key=` prefixes — a valid row looks exactly like:
`3	2026-06-11T14:02Z	21	2035336	35	unknown`
(your step number and values vary; the format doesn't).
