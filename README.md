# my-reporter

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
appends a prose paragraph under the tables; against `NoopEngine` it degrades to
digest-only. The `gh issue comment` side effect runs through `Policy`
(`ALLOW` by default). MyReporter never edits the tree or opens a PR.

## Usage

```bash
myreporter digest [--since 2026-07-01T00:00:00Z]
myreporter post --issue 12 --repo owner/name [--summarize]
```

## Install (development)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ../mythings-core -e ".[dev]"
pytest
```

## License

MIT — see [`LICENSE`](LICENSE).
