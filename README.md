# code-migration-kit-with-codex

A Codex adaptation of [Anthropic's code migration kit](https://github.com/anthropics/code-migration-kit-with-claude-code),
based on upstream commit `cf91c9d5068d9aaf95a36164169f08c3e636c909`.
It preserves the six-step migration process and portable scripts, with Codex
instructions, a repository skill, and native execution-rule templates.
This is an independent adaptation, not an official OpenAI or Anthropic product.

中文快速入门：[README.zh-CN.md](README.zh-CN.md)。

## Source and attribution

This project is derived from **Anthropic's
[code-migration-kit-with-claude-code](https://github.com/anthropics/code-migration-kit-with-claude-code)**.
The original migration methodology, prompts, scripts, templates, fixtures, and
historical examples come from that repository. This adaptation changes the
agent instructions, skill discovery, execution rules, and workflow guidance for
Codex, and adds Chinese documentation and offline checks.

The original Apache-2.0 license and Anthropic copyright notices are retained.
See [LICENSE](LICENSE). Upstream history is preserved for traceability.

This adaptation: [naikokodayo/code-migration-kit-with-codex](https://github.com/naikokodayo/code-migration-kit-with-codex).
The Codex-specific adaptation and its migration checks were developed with
[Codex](https://github.com/apps/chatgpt-codex-connector) assistance; the
upstream authors remain credited for the original kit.

This kit defaults to **structure-preserving migrations** — same architecture,
same data structures, new language. That's the case where the process below is
mechanical enough to template. If you're redesigning as you migrate, read
[If you're redesigning](#if-youre-redesigning) first: parts of this kit change,
and one part becomes invalid.

> **Provenance:** these prompts are reconstructions — generalized and reviewed
> against real production migrations, including Bun's 1M+ line Zig→Rust port,
> not transcripts. The real artifacts were messier and more specific: the Bun
> port's "prompt" was a 576-line rulebook
> ([PORTING.md](https://github.com/oven-sh/bun/commit/46d3bc29f270fa881dd5730ef1549e88407701a5))
> and a one-sentence kickoff.

> **Status:** Reference code. `RUN-NOTES.md` and `examples/` are preserved
> upstream history, not evidence of a Codex end-to-end migration. The Tig entry
> in `RUN-NOTES.md` records a Codex feasibility-only assessment. Local checks
> cover script fixtures, skill structure, and rule matching; see below.

## Quick start

Requires Python 3, Node.js, Bash (for the build daemon), and a current Codex
installation. No Claude account, SDK, or API integration is required.

1. Put this adapted kit inside or adjacent to the repository you are migrating.
   In the commands below, set `KIT` to its absolute path and run from the
   **target repository root**.
2. Merge this kit's `AGENTS.md` into the target's existing `AGENTS.md`, preserving
   project instructions. If none exists, copy it. Adjust kit-relative paths to
   your kit location. Codex reads `AGENTS.md`; an `@`-import is not required.
3. Link the skill into the target repository (do not overwrite an existing skill):
   ```sh
   KIT=/absolute/path/to/code-migration-kit-with-codex
   mkdir -p .agents/skills
   ln -s "$KIT/.agents/skills/code-migration" .agents/skills/code-migration
   ```
   Keep the full kit at that path; copying only `SKILL.md` loses its resources.
   If working in the kit itself, the skill is already discoverable; skip the link.
4. Open the target repository in Codex. Invoke `$code-migration` with the target
   language, or ask Codex to read `prompts/00-feasibility.md` from the kit and
   fill its placeholders. Stop at the feasibility verdict.
5. Validate the behavioral judge before Step 1. Use `prompts/00b-judge-setup.md`
   if the existing suite needs adaptation or lacks documented judge validation.
   Executable-level tests can still miss terminal behavior or select the wrong binary.
6. Before prompt 03, the human adapts and installs `templates/migration.rules`
   into the target's `.codex/rules/migration.rules`, then restarts Codex with
   the project config trusted. Follow [the rule setup and limitations](templates/rules.README.md).
   Do not install the loop bans before feasibility or judge setup: those phases
   need to measure builds and validate tests. Never mistake a file's presence
   for proof of runtime enforcement.
7. Run prompts 01–06 in order, one gate at a time. Select available models at
   the feasibility gate; the kit does not hardcode a model ID or change your
   global Codex configuration.

## Local validation

From the kit root, run `python3 scripts/check_kit.py`. This uses the original
Python, JS/TS, and C fixtures, exercises the manifest, queue and build daemon,
and validates rule decisions with `codex execpolicy check`. It does not call
an AI model. It does not prove live sandbox enforcement or migration quality.

Official references: [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[skills](https://learn.chatgpt.com/docs/build-skills),
[rules](https://learn.chatgpt.com/docs/agent-configuration/rules), and
[subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## Should you migrate at all?

Start with `prompts/00-feasibility.md`. Paste it into Codex in your repo.
It produces a read-only report: the case for leaving, three committed calls
(structure-preserving or redesign, what verification costs, whether your tests
survive), an evidence-backed scan of reusable target-language code, a sketch
of the six steps for your repo, and a verdict. "Don't
migrate" is a valid outcome. Nothing else in this kit matters until that
report says go.

## The six steps

Every step below follows the same doctrine: **you don't fix the code — you fix
the process that produced the code.** Individual failures get burned down by
fixer agents; recurring failures indict a rule, and the rule gets amended.

| Step | What happens | Kit artifact |
|---|---|---|
| 1. Create the map and the rules | Dependency map orders the work; gap inventory traces what the target language demands; the rulebook decides every translation question once | `scripts/depmap_*`, `prompts/01`, `prompts/02`, `templates/RULEBOOK.md`, `templates/inventory.tsv` |
| 2. Stress-test the rules | Dual-translation bakeoff + pilot run on a handful of nasty files; the only surviving output is rule changes | `prompts/03-stress-test.md` |
| 3. Translate everything | Implementer + two adversarial reviewers + fixer per unit, fanned out over a mechanical queue; the compiler waits | `prompts/04-translation-kickoff.md`, `scripts/queue_runner.mjs` |
| 4. Compile | One survey build grades everything; error list becomes a machine queue sliced by module; fixers work without compiler access | `prompts/05-survey-build.md`, `templates/migration.rules` (the bans) |
| 5. Run it | Hello world, then smoke tests — the cheap end-to-end proof before the expensive one | — |
| 6. Match behavior | Inherited test suite burndown, or build a parity referee against the old code | your existing test suite is the artifact; `prompts/06-post-parity.md` after the gate |

### Step 1 — Create the map and the rules

Three artifacts, built in parallel, audited together:

1. **The rulebook** (`templates/RULEBOOK.md` — copy it to
   `migration/RULEBOOK.md` in the target repo): every decision a translator could
   make two ways, decided once. The meta-rule: *if two agents could answer
   differently, it goes in the rulebook.* Draft it in a conversation with
   Codex, then have agents survey the codebase for the facts ("how many struct
   fields," "how many uses tree-wide") and adversarial reviewers audit it — one
   mistake class each.
2. **The dependency map** (`scripts/depmap_*.py|.mjs` + `prompts/01`): a
   deterministic script, not agent judgment. Orders the work, finds the cycles
   — at file granularity AND at the target's package granularity. (Bun's port
   had a clean file graph and still hit ~16K compile errors from package-level
   cycles nobody had checked.)
3. **The gap inventory** (`prompts/02` + `templates/inventory.tsv`): one flat
   table of every site where the target language demands something the source
   let you keep in your head — ownership, lifetimes, nullability, interface
   contracts. Implementers grep it; nobody reads it top to bottom.

The sign-off gates in these prompts work like this: a workflow runs its phase
to completion, returns the evidence, and exits. **Your sign-off is the act of
kicking off the next one.** Every queue is defined by what exists on disk, so
stopping is free and resuming is a re-invocation, not a recovery. When a
prompt says "use a workflow," it means: run the phase as parallel subagents
that complete and stop at the gate — use Codex subagents with disjoint write scopes and fresh reviewer contexts.
If unavailable, run independent Codex sessions over the same disk artifacts.
See `AGENTS.md` for context isolation and model-selection requirements.

### Step 2 — Stress-test the rules

The rulebook has never met real code. Before any fan-out:
**bakeoff** (two translators, separate contexts — one follows the rules, one
never learns they exist; a diff inspector turns every difference into a verdict
on a rule) and **pilot** (the production pipeline exactly as the fan-out will
run it, graded on obedience, not output quality). Amendments are queued for
you, never self-applied. See `prompts/03-stress-test.md`.

### Step 3 — Translate everything

The kickoff prompt is deliberately short (`prompts/04`) because by now the
rulebook is the prompt. The queue is mechanical: every manifest entry with no
output file on disk yet (`scripts/queue_runner.mjs`) —
`migration/manifest.tsv` is a Step 1 output, generated by prompt 01's
closing action from the dependency map's order with
`scripts/make_manifest.py`. Don't run the compiler — it grades everything next
step. Keep expensive operations out of loops using the execution rules and
separate human-started build process in `templates/rules.README.md`. The rules
template is `templates/migration.rules`, copied to the target repo's `.codex/rules/migration.rules`
by you before prompt 03 (Step 2's pilot needs the denies live), active
through Step 4 (prompt 05), test denies re-activated for Step 6's fix loops
(see `templates/rules.README.md`).

### Step 4 — Compile

One scripted **survey build** runs the compiler across everything and emits the
error list as a machine queue, sliced by module, leaves-to-root. Parallel
fixers work the queue **without compiler access** — the daemon that owns the
build is the only process that runs it. Repeat until clean.
`prompts/05-survey-build.md` runs this step. With denies active the standard
transport is `scripts/build_daemon.sh`: the human starts it once, it reruns
the build when the tree changes, and fixers consume the numbered
`migration/build-output-rN.txt` files. In one early test a human relayed every
build by hand — fine for a couple of rounds, not for fifty.

**If your target's typecheck is cheap (TypeScript, Go), this step dissolves
into Step 3** — run the typechecker inside every unit's loop instead of
batching it. The rule: every referee has a price, and the price decides its
position in the loop. Dissolving is an edit to the installed
`.codex/rules/migration.rules` at the gate — remove the typecheck denies and restart Codex before the loop
may run it. Verify installation before making this change. An upstream run
skipped its original permission setup entirely; the same process failure must
not become a silent waiver here.

### Step 5 — Run it

Hello world. Then the smallest end-to-end command your binary supports. Cheap
proofs before expensive ones.

### Step 6 — Match behavior

This is where the judge you set up before Step 1 does its job. If your old tests
hit the public surface (CLI, API, exported interface) they were your judge from
the start — run them against the new code, triage every failure by also running
it against the *old* code (regression / inherited / environment), and burn the
queue down. If your tests import source-language internals, the portable parity
harness you built with `prompts/00b-judge-setup.md` is the judge — run it against
both old and new and diff the results. Either way the old code is the executable
spec, the judge was validated against deliberately broken code before you trusted
it, and you've kept it running the whole migration. **Keep it running until the
end.**

The done-gate is explicit: every test in the parity referee passes, AND the
original suite has been re-run on the original code with zero inherited
failures — both counts documented in the report. For redesign migrations with no inherited suite, the gate is the
built parity referee's scenario list, signed off by the human. After the
gate, `prompts/06-post-parity.md` burns down the deferred `BUG(port)` /
`TODO(port)` / `PERF(port)` markers — each fix its own flagged change, proved
by a parity re-run.

One lesson from early testing: debug the referee before believing its verdicts.
In one run, all reported divergences were false — traced to two comparator bugs
(whitespace handling; JSON.stringify converting NaN/-Infinity to null), none to
the port. A referee that fails everything is usually broken, not right.

## If you're redesigning

Three things change and one thing breaks:

- The rulebook becomes a **design document** (what the new architecture is),
  not a lookup table (how each construct translates).
- The **bakeoff is invalid** — a diff between rule-following and native
  translations measures your redesign, not your rules. Substitute: adversarial
  review of the design doc itself, plus disposable full runs — run the whole
  migration cheaply, review what came out, fix the rules, throw the run away.
- The unit of work is a module or subsystem, not a file.
- Behavior matching still works unchanged — it never sees your internals.

## When you don't need this kit

JavaScript→TypeScript is the most common migration by volume, and you mostly
don't need any of this: TypeScript is a superset, adoption can be incremental,
file by file, with no parallel codebase. Use this kit when the move is total —
when every file must cross and the old language ends up deleted.

## What's in the box

```
prompts/         eight paste-ready prompts (00-feasibility, 00b-judge-setup → 06-post-parity)
templates/       RULEBOOK.md, inventory.tsv, migration.rules (+ setup, limitations, and rationale)
scripts/         dependency mappers (Python, JS/TS, C headers) + queue runner + manifest builder + build daemon
fixtures/        test trees + expected outputs for every script
.agents/skills/code-migration/  the Codex skill that walks the six steps
examples/        a complete example run — filled-in rulebook, inventory, diff report, parity scripts
AGENTS.md        the operating manual Codex reads when opened here
RUN-NOTES.md     historical upstream receipts (not Codex validation)
```

## A note on cost and rate limits

A production-scale port can consume billions of input tokens inside two weeks.
The process
works at any rate limit — the calendar doesn't. At standard API limits, expect
the same steps across a longer wall clock. Budget with a visible
multiplication: units of work × per-unit estimate, never a vibes number. And
weigh the figure against what the spend buys: most of the multiplier is the
review topology, and in testing that's where the catches came from (RUN-NOTES).

## Contributing

The upstream is reference code and does not monitor issues or PRs. This local
adaptation has not been published. You can fork it for your ecosystem.

## License

Apache-2.0 — see [LICENSE](LICENSE).
