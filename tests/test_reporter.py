from __future__ import annotations

from pathlib import Path

from mythings.engine import EngineResult
from mythings.ledger import Ledger

from conftest import entry, gh_comment, make_ledgers
from myreporter.reporter import Reporter


class SpyEngine:
    def __init__(self, reply: str) -> None:
        self.calls: list[str] = []
        self.reply = reply

    def run(self, request) -> EngineResult:
        self.calls.append(request.prompt)
        return EngineResult(text=self.reply)


def test_digest_counts_and_lists_decisions_verbatim(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[
            entry("mytester", "run", "success", "cover pkg:f", ts="2026-07-06T01:00:00Z", pr=7),
            entry("mytester", "run", "skipped", "fully covered", ts="2026-07-06T02:00:00Z"),
        ],
        dev=[
            entry("claude-code", "ship", "success", "released v0.0.1", ts="2026-07-06T00:30:00Z"),
            entry("claude-code", "decision", "success", "chose JSON over YAML"),
        ],
    )
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest().markdown

    assert "**4 ledger entries.**" in md
    assert "| mytester | 2 |" in md
    assert "| success | 3 |" in md
    assert "chose JSON over YAML" in md  # decision verbatim
    assert "released v0.0.1" in md  # ship verbatim
    assert "#7" in md  # pending PR (no later resolved entry)


def test_digest_sums_usage_and_flags_friction(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[
            entry("fleet_dispatch", "usage", "success", "run 1", ts="2026-07-07T01:00:00Z",
                  cost_usd=0.48, wasted_output_tokens=120, denials_count=10),
            entry("fleet_dispatch", "self_edit", "widened_allowlist", "added pytest variants",
                  ts="2026-07-07T01:00:01Z"),
            entry("fleet_dispatch", "friction", "needs_review", "unrecognized: curl",
                  ts="2026-07-07T01:00:02Z"),
        ],
        dev=[],
    )
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest().markdown

    assert "## Usage & waste" in md
    assert "1 run(s), $0.48 total cost" in md
    assert "10 permission denial(s), ~120 output tokens wasted" in md
    assert "1 auto-widened allowlist change(s)" in md
    assert "1 friction signal(s) awaiting human review" in md


def test_empty_window_is_graceful_and_still_writes_report(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(tmp_path, shared=[], dev=[])
    fake = gh_comment()
    reporter = Reporter(
        ledger_path=ledger_path, repo_root=repo_root, repo="owner/name", runner=fake
    )

    result = reporter.post(issue=9)

    assert "Nothing to report" in result.markdown
    assert any(c[:2] == ["issue", "comment"] for c in fake.calls)
    written = [e for e in Ledger(ledger_path) if e.kind == "report"]
    assert len(written) == 1
    assert written[0].outcome == "success"
    assert written[0].data["entries_count"] == 0
    assert written[0].data["comment_url"].endswith("issuecomment-123")


def test_since_last_report_is_incremental(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[
            entry("claude-code", "build", "success", "old work", ts="2026-07-01T00:00:00Z"),
            entry("myreporter", "report", "success", "prior", ts="2026-07-05T00:00:00Z",
                  window_end="2026-07-05T00:00:00Z"),
            entry("mytester", "run", "success", "new work", ts="2026-07-06T00:00:00Z"),
        ],
        dev=[],
    )
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest().markdown

    assert "old work" not in md  # before the last report's window_end, excluded
    assert "| run | 1 |" in md  # the new post-report run is counted


def test_summarize_appends_prose(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[entry("mytester", "run", "success", "cover pkg:f", ts="2026-07-06T01:00:00Z")],
        dev=[],
    )
    engine = SpyEngine(reply="Two runs happened this week.")
    reporter = Reporter(ledger_path=ledger_path, repo_root=repo_root, engine=engine)

    result = reporter.digest(summarize=True)

    assert len(engine.calls) == 1
    assert "## Summary" in result.markdown
    assert "Two runs happened this week." in result.markdown


def test_handoff_surfaces_open_threads_decisions_and_last_ship(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[
            entry("mytester", "run", "success", "cover pkg:f", ts="2026-07-06T01:00:00Z", pr=7),
            entry("myguard", "ask", "success", "destructive push needs sign-off",
                  ts="2026-07-06T01:30:00Z"),
        ],
        dev=[
            entry("claude-code", "decision", "success", "chose JSON over YAML",
                  ts="2026-07-06T00:30:00Z"),
            entry("claude-code", "ship", "success", "released v0.0.1", ts="2026-07-06T00:45:00Z"),
        ],
    )
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest(handoff=True).markdown

    assert "resume context" in md
    assert "## Open threads" in md
    assert "destructive push needs sign-off" in md
    assert "## Recent decisions" in md
    assert "chose JSON over YAML" in md
    assert "## Pending PRs" in md and "#7" in md
    assert "## Last shipped" in md and "released v0.0.1" in md
    assert "**4 ledger entries.**" not in md  # not the aggregate-digest layout


def test_handoff_surfaces_friction_as_open_thread(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[
            entry("fleet_dispatch", "friction", "needs_review", "unrecognized: curl -sSL foo",
                  ts="2026-07-07T01:00:00Z"),
        ],
        dev=[],
    )
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest(handoff=True).markdown

    assert "## Open threads" in md
    assert "unrecognized: curl -sSL foo" in md


def test_handoff_empty_window_reports_clean_baseline(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(tmp_path, shared=[], dev=[])
    md = Reporter(ledger_path=ledger_path, repo_root=repo_root).digest(handoff=True).markdown

    assert "Clean baseline" in md


def test_summarize_degrades_to_digest_only_on_empty_reply(tmp_path: Path) -> None:
    ledger_path, repo_root = make_ledgers(
        tmp_path,
        shared=[entry("mytester", "run", "success", "cover pkg:f", ts="2026-07-06T01:00:00Z")],
        dev=[],
    )
    engine = SpyEngine(reply="")  # NoopEngine-like
    reporter = Reporter(ledger_path=ledger_path, repo_root=repo_root, engine=engine)
    result = reporter.digest(summarize=True)

    assert len(engine.calls) == 1
    assert "## Summary" not in result.markdown  # still a complete digest
