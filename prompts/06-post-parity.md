# 06 — Post-parity burndown

<!-- Modified for the Codex adaptation; see README.md for provenance. -->

**When:** only after the Step 6 done-gate — every parity test passing AND the
original suite re-run clean on the original code, both counts documented (see
README Step 6). Never alongside it. **Prerequisites:** Step 6 report with
both counts. **Placeholders:** `[target tree]`, `[reviewer model]` (from the
Model plan signed off at the feasibility gate).

---

Use a workflow. The port shipped bug-for-bug; the markers are everything it
deferred. Collect every `BUG(port)`, `TODO(port)`, and `PERF(port)` marker
from [target tree] — mechanical grep, not memory — and open the report with
the per-marker counts as a receipt: the grep output, not a narrated total.

Classify every marker: **fix now** or **document and close**, one line of
reasoning per call. Document-and-close rows get their resolution written next
to the marker, and the marker comes out in one reviewed change.

Every fix-now ships as its own flagged change — one marker, one change. Each
re-runs the parity referee and proves the ONLY behavior that changed is the
marked defect; a fix that moves any other output is two changes, and a failed
review. Reviewers run on [reviewer model], per the Model plan — inheriting
the session default is a deviation; log it. A recurring marker pattern is a
rulebook indictment, same as ever: queue the amendment for me.

After a target module replaces the old implementation and its parity gate
passes, remove target-side fallback code, adapters, and branches with no
remaining callers. Verify callers before deletion. Keep the runnable original
baseline and its evidence until the full migration is accepted.

For each `PERF(port)` fix or requested performance comparison, attach a
reproducible measurement receipt:

- Build both versions with production optimization (for example, optimized C
  and Rust `--release`). Record revisions, binary hashes, compiler versions,
  build flags, dependencies, platform, and exact commands. Never compare a
  debug target to an optimized original and call the ratio a language result.
- Run the same behavior and workload: identical fixtures, arguments, output
  mode, environment, and result consumption. Verify outputs and exit status
  with the parity judge before timing. Link original assertions to their
  adapter routes and record any original-language helper still used by the
  target run. Mixed routes measure only the target component actually reached.
  Record any unsupported observables; extra generated
  scenarios do not substitute for missing original assertions.
- Control fixture setup as well as execution. For Git-backed suites, isolate
  system/global configuration and set `init.defaultBranch` to the value the
  original fixture expects before repository creation. Run both versions under
  that environment. Investigate original controls before touching expectations;
  a host-specific branch-name failure is not permission to weaken the test.
- Warm up consistently, alternate execution order, and retain repeated raw
  measurements plus their median and spread. State cache conditions and what
  is included: process startup, subprocesses, I/O, rendering, and build time.
  Keep build time separate from runtime; report microbenchmarks separately
  from representative end-to-end workloads. If memory was not measured, say so.
- Scope the conclusion to the measured component and behavior. A component
  benchmark or passing subset cannot close the full migration's parity gate.
  If requested before parity, store it as provisional component evidence and
  return to the current phase; do not enter this post-parity workflow early.
- Report safety independently from speed: first-party unsafe/FFI use and its
  enforcement, dependency unsafe/FFI exposure, and unreviewed boundaries.
  A first-party `forbid(unsafe_code)` lint does not establish an unsafe-free
  dependency graph or whole application.

Stop and show me the classification table and the per-fix parity results —
nothing merges until I sign off.
Append one timestamped line for this step to `migration/cost-log.tsv` —
create it with header `step\ttimestamp\twall_clock_min\ttokens\tsubagents\tmodel`
if absent; real values where available, `unknown` where not. Plain
tab-separated values, no `key=` prefixes — a valid row looks exactly like:
`3	2026-06-11T14:02Z	21	2035336	35	unknown`
(your step number and values vary; the format doesn't).
