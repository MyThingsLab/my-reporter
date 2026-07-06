from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from mythings._devledger import read_all
from mythings.ledger import Ledger, LedgerEntry

_HIGH_SIGNAL = ("ship", "decision")
_PR_RESOLVED = ("merged", "shipped", "closed")


@dataclass(frozen=True)
class Window:
    start: str | None  # ISO8601, inclusive; None = all-time
    end: str  # ISO8601, the moment the report was cut


@dataclass(frozen=True)
class Digest:
    window: Window
    entries: list[LedgerEntry] = field(default_factory=list)
    markdown: str = ""

    @property
    def count(self) -> int:
        return len(self.entries)


def load_entries(ledger_path: Path, repo_root: Path) -> list[LedgerEntry]:
    entries: list[LedgerEntry] = []
    if ledger_path.exists():
        entries.extend(Ledger(ledger_path))
    if (repo_root / "dev-ledger").is_dir():
        entries.extend(read_all(root=repo_root))
    entries.sort(key=lambda e: e.ts)
    return entries


def last_report_end(entries: list[LedgerEntry]) -> str | None:
    reports = [e for e in entries if e.tool == "myreporter" and e.kind == "report"]
    if not reports:
        return None
    latest = max(reports, key=lambda e: e.ts)
    return latest.data.get("window_end") or latest.ts


def in_window(entries: list[LedgerEntry], since: str | None) -> list[LedgerEntry]:
    if since is None:
        return list(entries)
    return [e for e in entries if e.ts >= since]


def _counts_table(title: str, counter: Counter[str]) -> str:
    if not counter:
        return ""
    rows = "\n".join(f"| {name} | {n} |" for name, n in sorted(counter.items()))
    return f"| {title} | count |\n|---|---|\n{rows}"


def pending_prs(entries: list[LedgerEntry]) -> list[tuple[str, LedgerEntry]]:
    # Latest entry mentioning each PR; pending unless that entry marks it resolved.
    latest: dict[str, LedgerEntry] = {}
    for e in entries:
        pr = e.data.get("pr")
        if pr:
            latest[str(pr)] = e
    out = []
    for pr, e in latest.items():
        if e.kind != "ship" and e.outcome not in _PR_RESOLVED:
            out.append((pr, e))
    return sorted(out, key=lambda item: item[0])


def _window_label(window: Window) -> str:
    return f"{window.start} → {window.end}" if window.start else f"all-time → {window.end}"


def render_markdown(entries: list[LedgerEntry], window: Window) -> str:
    parts = [f"# MyThingsLab report — {_window_label(window)}", ""]
    if not entries:
        parts.append("_Nothing to report in this window._")
        return "\n".join(parts)

    parts.append(f"**{len(entries)} ledger entries.**")
    for title, counter in (
        ("tool", Counter(e.tool for e in entries)),
        ("kind", Counter(e.kind for e in entries)),
        ("outcome", Counter(e.outcome for e in entries)),
    ):
        table = _counts_table(title, counter)
        if table:
            parts += ["", table]

    decisions = [e for e in entries if e.kind in _HIGH_SIGNAL]
    if decisions:
        parts += ["", "## Decisions & ships"]
        parts += [f"- `{e.ts}` **{e.tool}/{e.kind}**: {e.detail}" for e in decisions]

    pending = pending_prs(entries)
    if pending:
        parts += ["", "## Pending PRs"]
        parts += [f"- #{pr} ({e.tool}, `{e.ts}`)" for pr, e in pending]

    return "\n".join(parts)


def build_digest(entries: list[LedgerEntry], window: Window) -> Digest:
    windowed = in_window(entries, window.start)
    return Digest(window=window, entries=windowed, markdown=render_markdown(windowed, window))
