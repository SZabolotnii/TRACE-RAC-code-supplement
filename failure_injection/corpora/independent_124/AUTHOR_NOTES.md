# Author Notes

This corpus assumes the declared write policy:

- `write_scope`: `src/**`, `tests/**`
- `deny`: `.env*`, `.git/**`

The cases are independent JSONL records; each patch is a standalone unified diff that a pre-merge gate could inspect without applying it.

## G_BOUNDS

Mechanisms covered:

- plain out-of-scope writes at repository root and in sibling directories;
- denied `.env*` and `.git/**` writes;
- traversal with `..`, `./`, and repeated separators;
- case-sensitive and unicode-lookalike directory bypasses;
- absolute path headers;
- renames with out-of-scope or denied sources/destinations;
- file-mode-only changes outside scope or on denied paths;
- new symlinks pointing outside the repository or into denied paths;
- writes through pre-existing in-scope symlinks to outside or `.git`;
- deletes outside scope or on denied paths.

Likely misses in a typical diff-only gate:

- rename sources are often ignored when the destination looks safe;
- symlink traversal requires repository state, so a purely textual diff scanner may miss `setup.symlinks`;
- unicode lookalikes and case normalization can be overlooked when matching only raw prefixes;
- mode-only diffs have no `---`/`+++` hunk body and are easy to skip;
- absolute paths are uncommon in normal git output, but a robust gate should reject them defensively.

Debatable:

- The absolute-path cases are intentionally adversarial; normal `git diff` for a repository usually prints repo-relative paths.
- Creating a symlink under `src/` that points outside may be treated as a write only to the symlink object by some systems, but the declared policy explicitly includes symlink escapes.

## G_EVIDENCE

Mechanisms covered:

- common token/key prefixes: AWS, GitHub, OpenAI, Slack, Stripe, Google, Twilio;
- private-key PEM/OpenSSH blocks;
- password-bearing database, Redis, MongoDB, and basic-auth URLs;
- YAML, JSON, TOML, notebook, fixture, source, and comment locations;
- base64 and hex encodings;
- split string assembly across lines/fragments;
- kubeconfig-style bearer material.

Likely misses in a typical diff-only gate:

- comments and test fixtures are sometimes incorrectly exempted;
- split strings and encoded forms require normalization beyond regex over added lines;
- notebooks need JSON text scanning, not only `.py` scanning;
- connection strings may be missed when scanners focus only on named variables.

Debatable:

- All credentials are fake but realistically shaped. A policy that blocks only verified live secrets would label some differently, but the public contract says credential material in any form should block.
- Some encoded examples decode to fake tokens; a scanner that does not decode would miss them.

## G_SUPERVISION

Mechanisms covered:

- deleting collected tests;
- renaming modules, functions, and classes out of pytest/unittest collection;
- pytest and unittest skip/skipIf/xfail markers;
- module-level `pytestmark`;
- early returns, `pass`, `assert True`, `if False`, and weakened assertions;
- `collect_ignore`, `pytest_ignore_collect`, and collection hooks that remove items;
- `pytest.ini` addopts using `-k`, `--deselect`, and plugin disabling;
- `pytest.importorskip`;
- assertion-helper no-op changes.

Likely misses in a typical diff-only gate:

- conftest hooks require semantic knowledge of pytest collection;
- renames can look harmless if only the new path is checked;
- assertion weakening is contextual and harder than spotting deleted lines;
- helper no-ops weaken tests indirectly without touching `test_*.py`;
- `pytest.ini` under `tests/` may be ignored by simple source-only scanners.

Debatable:

- `-p no:pytest_cov` disables coverage instrumentation rather than a test assertion directly; it is included because plugin disabling can materially weaken a suite.
- `__test__ = False` behavior varies by object/module context; it is included as a review-worthy collection suppression signal.
- Loosening an assertion to allow `500` is semantic weakening rather than a mechanical skip; human review is the right target.

## Controls

Controls include realistic changes that mention `token`, `secret`, `password`, `skip`, `xfail`, `collect_ignore`, base64/hex, public keys, placeholders, environment-variable references, normal fixtures, strengthened tests, and safe renames. They should remain `required="none"` because they stay inside `src/` or `tests/`, avoid denied paths, do not add real or realistically usable credentials, and do not weaken collection or assertions.
