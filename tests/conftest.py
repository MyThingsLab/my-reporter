from __future__ import annotations

from pathlib import Path

from mythings.ledger import LedgerEntry
from mythings.testing import FakeGh
from mythings.testing import ledger_entry as entry
from mythings.testing import make_ledgers as _make_ledgers

# Shared fakes come from the core module; only my-reporter's domain wiring
# (the comment URL, the tmp_path/"repo" root shape) lives here. No
# `pytest_plugins` line: this suite uses only the plain helpers, and a
# top-level import alongside plugin registration would skip assertion
# rewriting for the module.

__all__ = ["FakeGh", "entry", "gh_comment", "make_ledgers"]


def gh_comment() -> FakeGh:
    # my-reporter's one side effect is `gh issue comment`.
    return FakeGh({("issue", "comment"): "https://github.com/owner/name/issues/9#issuecomment-123\n"})


def make_ledgers(
    tmp_path: Path, shared: list[LedgerEntry], dev: list[LedgerEntry]
) -> tuple[Path, Path]:
    return _make_ledgers(tmp_path / "repo", shared=shared, dev=dev)
