from __future__ import annotations

from pathlib import Path

import pytest
from mythings.engine import ClaudeCLIEngine, NoopEngine

from conftest import entry, make_ledgers
from myreporter.cli import _ENGINES, main


def test_engine_choices_map_to_expected_classes() -> None:
    assert _ENGINES["noop"] is NoopEngine
    assert _ENGINES["claude-cli"] is ClaudeCLIEngine


def test_post_defaults_to_noop_engine_and_summarize_is_a_noop(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo_root = make_ledgers(
        tmp_path, shared=[entry("mytester", "run", "success", "cover pkg:f")], dev=[]
    )
    monkeypatch.chdir(repo_root)
    # No --repo: Reporter._comment short-circuits before any `gh` subprocess runs.
    exit_code = main(
        ["post", "--issue", "1", "--summarize", "--repo-root", str(repo_root)]
    )

    assert exit_code == 0
    assert "posted digest" in capsys.readouterr().out


def test_engine_flag_accepts_claude_cli_without_invoking_it_when_not_summarizing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo_root = make_ledgers(tmp_path, shared=[], dev=[])
    monkeypatch.chdir(repo_root)

    exit_code = main(
        ["post", "--issue", "1", "--engine", "claude-cli", "--repo-root", str(repo_root)]
    )

    assert exit_code == 0  # constructs ClaudeCLIEngine but .run() is never called
