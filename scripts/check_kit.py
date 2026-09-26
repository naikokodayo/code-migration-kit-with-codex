#!/usr/bin/env python3
"""Offline regression checks. Requires Python 3, Node.js, Bash, and Codex CLI."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT, expected=0):
    result = subprocess.run([str(a) for a in args], cwd=cwd, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == expected, (args, result.stdout, result.stderr)
    return result.stdout


def main():
    for tool in ('node', 'bash', 'codex'):
        assert shutil.which(tool), f'Required tool not found: {tool}'
    with tempfile.TemporaryDirectory(prefix='codex-kit-check-') as tmp:
        tmp = Path(tmp)
        skill_dir = ROOT / '.agents/skills/code-migration'
        linked_skill = tmp / 'linked-skill'
        linked_skill.symlink_to(skill_dir, target_is_directory=True)
        resolved_root = (linked_skill / 'SKILL.md').resolve().parents[3]
        assert resolved_root == ROOT
        for resource in ('README.md', 'AGENTS.md', 'prompts/00-feasibility.md',
                         'templates/migration.rules', 'scripts/queue_runner.mjs'):
            assert (resolved_root / resource).is_file(), resource
        print('PASS: linked skill resolves its full kit resources')
        for language, interpreter, script in (
            ('python', sys.executable, 'depmap_python.py'),
            ('ts', 'node', 'depmap_ts.mjs'),
            ('c', sys.executable, 'depmap_c.py'),
        ):
            fixture = ROOT / 'fixtures' / language
            out = tmp / language
            run(interpreter, ROOT / 'scripts' / script, '--root', fixture, '--out', out)
            for name in ('edges.tsv', 'cycles.txt', 'order.txt'):
                assert (out / name).read_bytes() == (fixture / ('expected_' + name)).read_bytes(), (language, name)
        print('PASS: Python, TS, C dependency fixtures')

        manifest = tmp / 'manifest.tsv'
        order = ROOT / 'fixtures/python/expected_order.txt'
        run(sys.executable, ROOT / 'scripts/make_manifest.py', '--order', order,
            '--out', manifest, '--sub', 'pkg/=ts/', '--sub', '.py=.ts')
        assert manifest.read_bytes() == (ROOT / 'fixtures/python/expected_manifest.tsv').read_bytes()
        rejected = tmp / 'rejected.tsv'
        run(sys.executable, ROOT / 'scripts/make_manifest.py', '--order', order,
            '--out', rejected, expected=1)
        assert not rejected.exists(), 'Unchanged source paths must not produce a manifest'
        print('PASS: manifest mapping and source-overwrite rejection')

        queue = ['node', ROOT / 'scripts/queue_runner.mjs', '--manifest', manifest]
        units = json.loads(run(*queue, 'next', cwd=tmp))
        assert len(units) > 1
        target = tmp / units[0]['target']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
        assert run(*queue, 'status', cwd=tmp).startswith(f'1/{len(units)} done')
        run(*queue, 'verify', cwd=tmp, expected=1)
        target.write_text('// translated fixture\n')
        run(*queue, 'verify', cwd=tmp)
        assert json.loads(run(*queue, 'next', '--batch', '1', cwd=tmp)) == units[1:2]
        print('PASS: queue resume, batching, and empty-output rejection')

        daemon = ['bash', ROOT / 'scripts/build_daemon.sh']
        run(*daemon, '--cmd', 'echo fixture-build', '--once', cwd=tmp)
        assert (tmp / 'migration/build-output-r1.txt').read_text() == 'fixture-build\n'
        report = run(*daemon, '--cmd', 'echo fixture-failure; exit 7', '--once', cwd=tmp)
        assert 'round 2: exit 7' in report
        assert (tmp / 'migration/build-output-r2.txt').read_text() == 'fixture-failure\n'
        run(*daemon, '--interval', '0', '--cmd', 'echo unused', '--once', cwd=tmp, expected=1)
        print('PASS: build output, round numbering, failure reporting, and interval validation')

    rules = ROOT / 'templates/migration.rules'
    # Independent expected behavior, not extracted from the policy under test.
    forbidden = [['git', command] for command in
                 ('rebase', 'reset', 'checkout', 'stash', 'push', 'commit',
                  'merge', 'switch', 'restore', 'clean')]
    forbidden += [['cargo', command] for command in ('build', 'check', 'test', 'run')]
    forbidden += [['npm', 'test'], ['npx', 'tsc'], ['make'], ['cmake']]
    for command in forbidden:
        decision = json.loads(run('codex', 'execpolicy', 'check', '--rules', rules, '--', *command))
        assert decision.get('decision') == 'forbidden', command
    for command in (['git', 'status'], ['git', 'diff'], ['git', 'log'], ['rg', 'TODO']):
        decision = json.loads(run('codex', 'execpolicy', 'check', '--rules', rules, '--', *command))
        assert not decision.get('matchedRules'), command
    print('PASS: 18 forbidden prefixes; read-only commands unchanged')
    print('All offline checks passed. Live Codex enforcement and end-to-end migration are not tested.')


if __name__ == '__main__':
    main()
