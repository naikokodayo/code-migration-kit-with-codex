# 03 — Stress-test the rules

<!-- Modified for the Codex adaptation; see README.md for provenance. -->

**When:** Step 2, after the rulebook, inventory, and dependency map are signed
off. **Prerequisites:** committed RULEBOOK.md and inventory; this prompt is
only valid for **structure-preserving** migrations — for redesigns the bakeoff
measures your redesign, not your rules (see README, "If you're redesigning").
**Placeholders:** `[3]` (file count), `[target language]`, `[target formatter]`,
`[implementer model]`, `[reviewer model]` — the last two from the Model plan
signed off at the feasibility gate.

---

Use a workflow. The **rulebook** has never met real code. Stress-test it on
[3] real files before translation fan-out. Nothing translated here ships;
the surviving outputs are evidence and proposed rule changes.

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

Second: set the model explicitly on every subagent call —
translators and the pilot implementer on [implementer model], reviewers and
the diff inspector on [reviewer model]; fixers ride [implementer model]
unless the Model plan says otherwise. Inheriting the session default is a
deviation; log it.

Pick the files by criteria, not taste: score candidates by how many of the
rulebook's riskiest sections and **gap inventory** rows they exercise, take
the top [3], and write the selection — with its scores and file:line proof —
to a report under `migration/stress-test/`, queueing its commit for me at
the gate — commits are denied in-loop by design. Easy files make a clean
diff and a useless step.

Then the **dual translators**, in separate contexts and separate workspaces.
Translator A works in a throwaway worktree on a branch that never merges. It
follows the rulebook to the letter, citing the rule behind every nontrivial
choice — and where the rulebook is silent, flags the silence inline instead of
inventing policy. Translator B gets a scratch directory outside the repo
containing only the [3] source files, copied out — not a checkout, so the
rulebook and inventory aren't on disk to find — and one instruction: port
these the way a fluent [target language] engineer would write them natively.
Start B in a fresh Codex session with no inherited conversation, kit skill,
or kit AGENTS.md. B must never see the rulebook or learn it exists — one glimpse and it stops
being a baseline.

A third context, the **diff inspector**, sees everything. Run both outputs
through [target formatter] first, so style noise never reaches it. Every
remaining difference becomes one row: the quoted lines from both versions, the
rule section it indicts — or the gap it exposes where the rulebook was silent —
and a verdict with evidence: rulebook right, native right, both defensible, or
both wrong. The rulebook is the defendant here, not the judge — but "native is
wrong" must stay sayable: a difference the rulebook wins indicts nothing, and
a report where every difference indicts a rule is as suspicious as one with
none.

In parallel, run the same [3] files through the **pilot run**: the production
pipeline exactly as the fan-out will use it — one **implementer**, two
adversarial **reviewers**, one **fixer**, same prompts, no special pilot
versions. The reviewers carry one extra standing question: did the implementer
follow the rulebook — citing the section for every deviation. A translation
that comes out right because the implementer quietly ignored the rules is a
failed pilot; the fan-out depends on obedience, not on three files going well.

Queue every proposed rule change for me with its evidence — never edit the
rulebook yourselves. Round 1 ends at the amendment queue: show me the queue
and the adherence findings — not the translations — retire both disposable workspaces —
archive A's managed worktree using the client tool where available and remove
only B's task-owned scratch directory — recording the cleanup in the report, and exit. Applying amendments is my act at the gate; a workflow that
waits mid-run for me is forbidden (AGENTS.md rule 3). After I apply them I
re-paste this prompt, and it resumes from disk state: if round-1 artifacts
already exist under `migration/stress-test/`, repeat the policy check, skip the old
file selection, and run the re-round — one more bakeoff on fresh files,
weighted toward the sections that just changed (re-running the same files
only proves the patch) — plus the pilot against the amended rules. Stop
early if the same section gets re-amended twice; that needs a decision from
me, not a third wording. The re-round ends at the same gate: amendment
queue, adherence findings, and the round-over-round delta. No fan-out starts
until I sign off. End the report with an estimated duration for the next
step (the translation fan-out) — wall-clock and active-attention minutes,
derived from the manifest size and the pilot's per-file timings.
Append one timestamped line for this step to `migration/cost-log.tsv` —
create it with header `step\ttimestamp\twall_clock_min\ttokens\tsubagents\tmodel`
if absent; real values where available, `unknown` where not. Plain
tab-separated values, no `key=` prefixes — a valid row looks exactly like:
`3	2026-06-11T14:02Z	21	2035336	35	unknown`
(your step number and values vary; the format doesn't).
