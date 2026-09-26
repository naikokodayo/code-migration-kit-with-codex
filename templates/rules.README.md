# Codex migration-loop rules

<!-- Modified from the upstream kit for Codex; see README.md for provenance. -->

`migration.rules` replaces the upstream Claude permission template with Codex
`prefix_rule(..., decision="forbidden")` entries. It preserves the original
18 blocked prefixes and intentionally adds no `allow` entries.

## Install at the gate, before prompt 03

The human chooses the build/test commands and the referee price. Run these
commands from the target repository root, with `KIT` pointing at the full kit:

```sh
KIT=/absolute/path/to/code-migration-kit-with-codex
mkdir -p .codex/rules
cp -i "$KIT/templates/migration.rules" .codex/rules/migration.rules
```

Inspect an existing file before replacing it. Adapt the prefixes to the actual
commands used by this migration: for example, add `go build`, `go test`, or
`python -m pytest` if those are your expensive commands. The template does not
claim to cover commands it does not list. Do not install these loop rules for
feasibility or judge setup, where builds and tests are required.

Restart Codex after installation or changes. Project-local rules load only
when the project's `.codex/` configuration layer is trusted; confirm this in
the client. Follow organizational policy if project rules are not supported.
Do not change sandbox or approval settings to make this template work.

Check the adapted file using the Codex CLI (these commands only evaluate the
policy; they do not execute the command after `--`):

```sh
codex execpolicy check --pretty --rules .codex/rules/migration.rules -- cargo build
codex execpolicy check --pretty --rules .codex/rules/migration.rules -- git reset --hard
codex execpolicy check --pretty --rules .codex/rules/migration.rules -- git status
```

The first two must report `forbidden`; `git status` must not be forbidden by
this file. Repeat with the real build/test commands after adapting the file.
The full template is also checked by `python3 scripts/check_kit.py` in the kit.
An offline check validates matching, not whether a running Codex session loaded
these rules. Record the installed path, checked commands, and the human's
trust/restart confirmation at the gate. Missing runtime evidence must remain
an explicit limitation, not be reported as successful enforcement.

## What these rules do and do not enforce

The [official rules documentation](https://learn.chatgpt.com/docs/agent-configuration/rules)
describes rules as controls for commands run **outside the sandbox**. They are
experimental, not a drop-in equivalent of Claude Code permissions. They do not
provide per-role filesystem protection or a universal ban on every tool call.
Argument prefixes also do not cover every spelling: wrappers, executable paths,
Git global options, and aliases can differ from the listed prefixes. Never use
such differences to bypass a restriction. Existing sandbox, approval, and
organization policies remain in effect.

For this kit's workflow, reviewers remain read-only, workers own disjoint files,
and only a separate **human-started** build daemon runs expensive commands.
If strict prevention of compiler access is required, use an isolated worker
environment without the compiler/build credentials; `.rules` alone cannot
promise that. Report missing isolation and obtain a human decision or explicit
waiver at the phase gate before fan-out.

## Why these commands are separated

- **Git mutations:** reset/checkout/clean can destroy another worker's changes.
  Commit, push, merge, branch/worktree setup, and cleanup belong at human-approved
  batch gates, outside restricted worker loops. Read-only Git operations are
  unaffected by this template, subject to existing policy.
- **Builds:** one survey build per round prevents redundant expensive builds
  and keeps translation focused on the rulebook. The human starts
  `bash "$KIT/scripts/build_daemon.sh" --cmd "cargo check --all-targets"`
  in a separate terminal at the target root. Workers only consume numbered
  `migration/build-output-rN.txt` files. Do not launch this wrapper from a
  restricted worker as a way around a rule.
- **Tests:** retain/re-enable expensive-test restrictions for parity-fix loops;
  the human-run referee executes tests and supplies failure evidence. Use the
  same separation for post-parity fixes.
- **Rulebook:** its read-only status inside loops is a prompt/review contract,
  not a filesystem guarantee. Review any in-loop rulebook edit as a violation.

A cheap typechecker can run inside a loop only after the human updates the
rulebook, removes its specific `forbidden` entry at a gate, and restarts Codex.
Adding an `allow` entry does not override `forbidden`: the strictest matching
rule wins. Other rules files or managed policy may still forbid the command.
The human retires the loop rules when the migration is complete; leaving them
active would also affect later Codex work in the target project.
