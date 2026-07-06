from __future__ import annotations

from pathlib import Path

from mythings.ledger import Ledger, LedgerEntry


class FakeRunner:
    # Mocks only the `gh` subprocess boundary (used by `post`).
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str]) -> str:
        self.calls.append(argv)
        if argv[:2] == ["issue", "comment"]:
            return "https://github.com/owner/name/issues/9#issuecomment-123\n"
        raise AssertionError(f"unexpected gh call: {argv}")


def entry(
    tool: str, kind: str, outcome: str, detail: str = "", ts: str = "", **data: object
) -> LedgerEntry:
    return LedgerEntry(
        tool=tool,
        kind=kind,
        outcome=outcome,
        detail=detail,
        ts=ts or "2026-07-06T00:00:00Z",
        data=data,
    )


def make_ledgers(
    tmp_path: Path, shared: list[LedgerEntry], dev: list[LedgerEntry]
) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    (repo_root / "dev-ledger").mkdir(parents=True)
    ledger_path = repo_root / ".mythings" / "ledger.jsonl"
    shared_ledger = Ledger(ledger_path)
    for e in shared:
        shared_ledger.append(e)
    dev_ledger = Ledger(repo_root / "dev-ledger" / "2026-07-06.jsonl")
    for e in dev:
        dev_ledger.append(e)
    return ledger_path, repo_root
