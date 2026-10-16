# External corpus for the authority-transition probe

Written 2026-10-06 by Codex (OpenAI `gpt-5.5`, reasoning effort high, codex-cli 0.156.1,
session `01a110fa-5c1c-7d73-bc11-a9bcd165c128`), working blind. It ran in an empty scratch
directory. It was told not to read anything outside that directory, and its command log
shows that it did not. It never saw the gate's code, the earlier corpora or any report.
Its only brief is `PROMPT.md`: the declared policy and the public contract of the three
gates.

This corpus is committed **before its first run**, so nothing in the gate can be tuned to
it. Any change to the gate made after a result on this corpus is in-sample from then on,
the same as the 174-mechanism corpus after 2026-10-02.

| File | sha256 |
|---|---|
| `cases.jsonl` | `fb8213c9c502b34bbaf5b2ab6c4faf2040eb1141eb32ef8c2d25b3c67ac8ab1b` |
| `AUTHOR_NOTES.md` | `b37416a507ce0cd8fbb01ede5790bb56f8eb4ee64c2975b121dff709950b4f7f` |
| `PROMPT.md` | `910c6f144f005c8f4b591ddd554c9c33e36f092234ed79d54293516946b16969` |

The counts, as Codex's own validator reported them: 124 cases, of which 79 are injected
(27 `G_BOUNDS`, 26 `G_EVIDENCE`, 26 `G_SUPERVISION`) and 45 are controls. The labels are
the author's. Cases the author called debatable are listed in `AUTHOR_NOTES.md` and are
kept in the corpus.

The credentials in it are invented. Some of them are shaped closely enough to real
formats that GitHub push protection or a secret scanner may flag the file. That is
intended.
