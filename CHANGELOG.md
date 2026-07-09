# Changelog

## [Unreleased]
### Added/Changed
- shipped MyReporter skeleton: deterministic ledger+dev-ledger digest (counts, decisions/ships verbatim, pending PRs), optional --summarize Engine prose (NoopEngine->digest-only), gh issue comment via Policy, kind=report ledger; ruff+pytest green (6 tests)
- Add --handoff mode: renders windowed entries as a resume-context brief (open threads, recent decisions, pending PRs, last ship) instead of the aggregate digest; reuses the existing --summarize Engine seam unchanged
- Wire --engine {noop,claude-cli} into the post command: --summarize now has a real backend option (ClaudeCLIEngine) alongside the existing NoopEngine default. Verified end-to-end with a live claude CLI call -- real prose landed under ## Summary, the fleet's first genuine judgment step
- Add --engine-model flag: build_engine(name, model) factory replaces the type[Engine] map so --engine claude-cli can pick a model (issue #7)
