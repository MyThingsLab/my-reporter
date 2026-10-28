# Changelog

## [Unreleased]
### Added/Changed
- shipped MyReporter skeleton: deterministic ledger+dev-ledger digest (counts, decisions/ships verbatim, pending PRs), optional --summarize Engine prose (NoopEngine->digest-only), gh issue comment via Policy, kind=report ledger; ruff+pytest green (6 tests)
- Add --handoff mode: renders windowed entries as a resume-context brief (open threads, recent decisions, pending PRs, last ship) instead of the aggregate digest; reuses the existing --summarize Engine seam unchanged
- Wire --engine {noop,claude-cli} into the post command: --summarize now has a real backend option (ClaudeCLIEngine) alongside the existing NoopEngine default. Verified end-to-end with a live claude CLI call -- real prose landed under ## Summary, the fleet's first genuine judgment step
- Add --engine-model flag: build_engine(name, model) factory replaces the type[Engine] map so --engine claude-cli can pick a model (issue #7)
- Pilot migration to mythings.testing: FakeRunner/entry/make_ledgers deleted from conftest, replaced by FakeGh/ledger_entry/make_ledgers imports; gh_comment() and the tmp_path/'repo' root shape stay local as domain wiring. No pytest_plugins line — this suite uses only plain helpers, and a top-level import alongside registration would skip assertion rewriting.
- Surface recent failures and blockers in handoff digests

All notable changes to `my-reporter` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
[semver](https://semver.org/), per the rules in `RELEASE.md`.

## [1.0.0] - 2026-07-20

First stable release. Baseline of the Ledger/dev-ledger digest and comment
posting as it already existed. No behavior changes in this release — it
exists to establish the tag downstream repos pin against. Adopts the v1
release contract (`RELEASE.md`) and pins its own `my-things-core` dependency
to `@v1.0.0` instead of floating on `@main`.
