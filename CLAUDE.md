# my-reporter — agent instructions

You are developing **my-reporter**, a MyThingsLab My[X] tool.

**Inherited rules:** obey [`./HARNESS.md`](./HARNESS.md) in full — the vendored
MyThingsLab build-harness rules. Do not restate or override them. Anything not
covered here defers to `HARNESS.md`, then `my-things-core/docs/CONVENTIONS.md`.

## This tool

- **Purpose:** reads the shared `Ledger` and each repo's `dev-ledger/`, and
  produces a markdown digest (counts by tool/kind/outcome, decisions/ships
  verbatim, pending PRs). Prints it, or posts it as a GitHub issue comment.
  `--handoff` renders the same windowed entries as a resume-context brief
  (open threads, recent decisions, pending PRs, last ship) for a new
  session/agent to read instead of re-deriving state from raw history.
- **The single Engine call:** optional. Deterministic by default. With
  `--summarize`, one Engine call turns the already-computed markdown digest into
  a prose paragraph appended under the tables — the model only rewrites the
  digest, it never sees raw ledger data to hallucinate against. Backend chosen
  via `--engine {noop,claude-cli}` (default `noop`). Against `NoopEngine`, or on
  a `ClaudeCLIEngine` failure, the reply is empty, so `--summarize` degrades to
  "digest only".
- **Invariants / rules:** read-only — never mutates other tools' ledger entries,
  never edits the repo tree, never opens a PR. Its one side effect is
  `gh issue comment`, wrapped as `Action(kind="bash", ...)` through
  `Policy.evaluate` (`ALLOW` by default). Writes exactly one `kind=report` ledger
  entry per run, which makes "since last report" incremental.
- **Backlog label:** `my-reporter`.
