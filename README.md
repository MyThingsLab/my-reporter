# my-reporter

[![CI](https://github.com/MyThingsLab/my-reporter/actions/workflows/ci.yml/badge.svg)](https://github.com/MyThingsLab/my-reporter/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/MyThingsLab/my-reporter/branch/main/graph/badge.svg)](https://codecov.io/gh/MyThingsLab/my-reporter) ![Python](https://img.shields.io/badge/python-3.11%2B-blue) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Reads the shared `Ledger` and each repo's `dev-ledger/`, and produces a markdown
digest of build activity — counts by tool/kind/outcome, decisions and ships
verbatim, and pending PRs. Prints it, or posts it as a GitHub issue comment.

## How it works

1. Merge the shared `Ledger` and `dev-ledger/*.jsonl`, sorted by timestamp.
2. Filter to a window (`--since ISO8601`, default: since the last `kind=report`
   entry, else all-time).
3. Aggregate counts, list `ship`/`decision` entries verbatim, list pending PRs.
4. Render one markdown document.

`digest` prints to stdout (dev loop / CI job summary, read-only). `post`
comments the digest on an issue and writes a `kind=report` ledger entry (which
makes "since last report" incremental). With `--summarize`, one Engine call
appends a prose paragraph under the tables. The backend is `--engine
{noop,claude-cli}` (default `noop` — no tokens spent, no prose either).
`claude-cli` shells out to the `claude` CLI for a real judgment call; against
either engine's empty/failed reply, `--summarize` degrades to digest-only. The
`gh issue comment` side effect runs through `Policy` (`ALLOW` by default).
MyReporter never edits the tree or opens a PR.

With `--handoff`, the same merged/windowed entries render as a resume-context
brief instead of the aggregate digest: open threads (`kind=ask`/`kind=drift`),
the last few `kind=decision` entries verbatim, pending PRs, and the most recent
`kind=ship`. It's meant for a new session or agent to read instead of
re-deriving "what's going on" from raw git/ledger history — `--summarize` still
works on top of it, same Engine seam either way.

## Usage

```bash
myreporter digest [--since 2026-07-01T00:00:00Z] [--handoff]
myreporter post --issue 12 --repo owner/name [--summarize] [--engine noop|claude-cli] [--handoff]
```

## Install (development)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ../mythings-core -e ".[dev]"
pytest
```

## License

MIT — see [`LICENSE`](LICENSE).
