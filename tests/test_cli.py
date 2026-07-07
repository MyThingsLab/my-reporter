from __future__ import annotations

from pathlib import Path

import pytest
from mythings.engine import ClaudeCLIEngine, NoopEngine

from conftest import entry, make_ledgers
from myreporter.cli import build_engine, main


def test_build_engine_maps_names_to_expected_backends() -> None:
    assert isinstance(build_engine("noop"), NoopEngine)
    assert isinstance(build_engine("claude-cli"), ClaudeCLIEngine)


def test_build_engine_passes_model_through_to_claude_cli() -> None:
    engine = build_engine("claude-cli", model="haiku")
    assert isinstance(engine, ClaudeCLIEngine)
    assert engine._model == "haiku"


def test_digest_prints_markdown_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo_root = make_ledgers(
        tmp_path, shared=[entry("mytester", "run", "success", "cover pkg:f")], dev=[]
    )
    monkeypatch.chdir(repo_root)

    exit_code = main(["digest", "--repo-root", str(repo_root)])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "MyThingsLab report" in out
    assert "mytester" in out


def test_digest_handoff_renders_the_handoff_brief(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo_root = make_ledgers(
        tmp_path, shared=[entry("mytester", "run", "success", "cover pkg:f")], dev=[]
    )
    monkeypatch.chdir(repo_root)

    exit_code = main(["digest", "--handoff", "--repo-root", str(repo_root)])

    assert exit_code == 0
    assert capsys.readouterr().out.strip()  # a non-empty brief was rendered


def test_post_handoff_reports_the_handoff_mode(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo_root = make_ledgers(
        tmp_path, shared=[entry("mytester", "run", "success", "cover pkg:f")], dev=[]
    )
    monkeypatch.chdir(repo_root)
    # No --repo: Reporter._comment short-circuits before any `gh` subprocess runs.
    exit_code = main(["post", "--issue", "1", "--handoff", "--repo-root", str(repo_root)])

    assert exit_code == 0
    assert "posted handoff" in capsys.readouterr().out


def test_missing_subcommand_is_a_usage_error() -> None:
    with pytest.raises(SystemExit):
        main([])


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
