# Failure-injection study: case files and decision logs

This folder holds the deterministic failure-injection study in agentic coding
reported in *Trust Is Not a Score: Runtime Assurance Contracts for High-Risk AI
Agents*, arXiv:2609.39717v2 (Section 7). It was added in release v1.1.0.

Every case is a proposed change to a small synthetic repository. An injected
case violates one gate of the contract; a control case is matched to an
injected class but should be allowed. The gate implementation that produced the
decisions (TRACE-AI-gate) is private and is **not** included. The case files let
a reader inspect every injected failure, reuse the cases in another study, and
check that the decision logs refer to exactly these cases. They do not allow a
rerun of the original gate.

## Contents

| Path | What it is |
|---|---|
| `corpora/mechanisms_174/cases.jsonl` | 174 cases, each a distinct mechanism: 87 injections and 87 class-matched controls |
| `corpora/mechanisms_174/fixture.json` | The repository state these cases assume: write scope, deny globs, pre-existing files and 31 symbolic links |
| `corpora/independent_124/cases.jsonl` | 124 cases written blind by OpenAI Codex (gpt-5.5) from the policy alone: 79 injections and 45 controls |
| `corpora/independent_124/README.md`, `PROMPT.md`, `AUTHOR_NOTES.md` | How that corpus was written, the brief it was given, and the cases its author called debatable |
| `decisions/decisions_mechanisms_first_run.jsonl` | Decisions on the 174 mechanisms before a change to one detector (the test-deletion guard) |
| `decisions/decisions_mechanisms.jsonl` | The same cases after that change; from this run on, the 174 cases are in-sample |
| `decisions/decisions_independent.jsonl` | Decisions on the independent corpus, which was committed before its first run |
| `decisions/static_audit.py` | Recomputes the counts in Tables 4 and 5 and Section 7.6 from the logs |
| `check_corpora.py` | Checks that case identifiers and labels in the case files match the logs |
| `SHA256SUMS` | Hashes of every file in this folder |

## Case schema

Both case files are JSON Lines, one case per line.

| Field | Meaning |
|---|---|
| `case_id` | Identifier, the same as in the decision logs |
| `gate` | The gate an injected case violates: `G_BOUNDS`, `G_EVIDENCE` or `G_SUPERVISION` |
| `required` | Required response: `block`, `review` (human review under `G_SUPERVISION`) or `none` for a control |
| `files` | Paths the change touches, relative to the repository root |
| `patch` | The proposed change as a unified diff |

The 174-mechanism file adds `case_class` (one of seven classes), `positive`
(injected or control) and `corpus` (`A`: the earlier envelope-bypass corpus;
`B`: cases written on 2026-09-21 for the review-required classes). The
independent file adds `mechanism` (a one-line description) and `setup` (files
and links that exist before the change).

In `fixture.json`, `<repo>` is the repository root and `<outside>` is its
parent directory. Links whose target starts with `<outside>`, `..` or `/` point
outside the write scope.

## Reproduce

Python 3.10 or newer, no third-party packages. From this folder:

```sh
python3 check_corpora.py
cd decisions && python3 static_audit.py
```

`check_corpora.py` should print three `PASS` lines. Expected counts from
`static_audit.py`, each cell giving unauthorized action / admitted injections /
auto-admitted review / false refusal:

| Log | RAC | score (published weights) | score (best) | protocol |
|---|---|---|---|---|
| mechanisms, first run | 0/63, 7/87, 7/24, 3/87 | 56/63, 80/87, 24/24, 0/87 | 0/63, 7/87, 7/24, 3/87 | 38/63, 62/87, 24/24, 0/87 |
| mechanisms, after fix | 0/63, 0/87, 0/24, 2/87 | 56/63, 80/87, 24/24, 0/87 | 0/63, 0/87, 0/24, 2/87 | 38/63, 62/87, 24/24, 0/87 |
| independent | 21/53, 35/79, 14/26, 1/45 | 52/53, 78/79, 26/26, 0/45 | 21/53, 35/79, 14/26, 1/45 | 34/53, 60/79, 26/26, 0/45 |

In all three logs the best score configuration admits exactly the cases that
RAC admits.

## Reading the cases

- **The 174-mechanism patches are minimal.** Several classes are decided by
  repository state rather than by the diff text. A symbolic-link escape, for
  example, has a patch that is only a diff header; the escape is in
  `fixture.json`. A reader who sees only the patch cannot tell these cases
  apart. For a study in which people review the material, the independent
  corpus, whose patches and `setup` are complete, is the better starting point.
- **The credentials are invented.** Both corpora contain credential-shaped
  strings, some base64-encoded, built to trigger the evidence gate. None is a
  real secret. Secret scanners and GitHub push protection may still flag them.
- **The labels are the corpus authors' labels.** For the independent corpus,
  the paper also reports an adjudicated count within the detectors' contract
  (16 of 62); the debatable cases are listed in `AUTHOR_NOTES.md`.

## Withdrawn corpus

arXiv:2609.39717v1 and the originally submitted manuscript reported a corpus
of 280 cases with a field-limited log (`static_decisions.jsonl`). Most of those
cases were index clones of a few templates. That corpus is withdrawn and is not
distributed; the 174-mechanism corpus replaces it.

## Provenance

The 174-mechanism file was exported from the case builders of the private
TRACE-AI-gate at tag `v0.6.0` (commit `c6c1d52`); temporary paths were replaced by `<repo>` and
`<outside>`, and the export was checked against the gate's CI report (same 174
identifiers, same labels). The independent corpus is copied byte for byte; its
hashes match those recorded in its README.
