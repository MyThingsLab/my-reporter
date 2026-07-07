from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from mythings.engine import Engine, EngineRequest, NoopEngine
from mythings.github import Runner, _gh
from mythings.isolation import in_github_actions
from mythings.ledger import Ledger
from mythings.policy import ALLOW, Action, Decision, Policy, PolicyResult

from myreporter.digest import (
    Digest,
    Window,
    build_digest,
    last_report_end,
    load_entries,
)

_SUMMARIZE_SYSTEM = (
    "Rewrite this build-activity digest as one short prose paragraph. "
    "Use only the information already present; do not invent anything."
)


class _AllowPolicy:
    def evaluate(self, action: Action) -> PolicyResult:
        return ALLOW


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class Reporter:
    def __init__(
        self,
        *,
        ledger_path: str | Path,
        repo_root: str | Path = ".",
        repo: str | None = None,
        runner: Runner = _gh,
        engine: Engine | None = None,
        policy: Policy | None = None,
    ) -> None:
        self.ledger_path = Path(ledger_path)
        self.repo_root = Path(repo_root)
        self.repo = repo
        self.runner = runner
        self.ledger = Ledger(self.ledger_path)
        self.engine: Engine = engine or NoopEngine()
        self.policy: Policy = policy or _AllowPolicy()

    def digest(
        self,
        *,
        since: str | None = None,
        summarize: bool = False,
        handoff: bool = False,
    ) -> Digest:
        entries = load_entries(self.ledger_path, self.repo_root)
        start = since if since is not None else last_report_end(entries)
        result = build_digest(entries, Window(start=start, end=_now()), handoff=handoff)
        if summarize:
            result = self._summarize(result)
        return result

    def post(
        self,
        issue: int,
        *,
        since: str | None = None,
        summarize: bool = False,
        handoff: bool = False,
    ) -> Digest:
        result = self.digest(since=since, summarize=summarize, handoff=handoff)
        url = self._comment(issue, result.markdown)
        self._record(result, url, handoff=handoff)
        return result

    def _summarize(self, result: Digest) -> Digest:
        prose = self.engine.run(
            EngineRequest(prompt=result.markdown, system=_SUMMARIZE_SYSTEM)
        ).text.strip()
        if not prose:
            return result  # NoopEngine / empty reply: digest only, still complete
        return replace(result, markdown=f"{result.markdown}\n\n## Summary\n\n{prose}")

    def _comment(self, issue: int, body: str) -> str | None:
        if self.repo is None:
            return None
        argv = ["issue", "comment", str(issue), "--repo", self.repo, "--body", body]
        action = Action(kind="bash", payload={"command": "gh " + " ".join(argv[:3])})
        if self.policy.evaluate(action).under(unattended=in_github_actions()) is not Decision.ALLOW:
            return None
        return self.runner(argv).strip() or None

    def _record(self, result: Digest, comment_url: str | None, *, handoff: bool = False) -> None:
        mode = "handoff" if handoff else "digest"
        self.ledger.record(
            tool="myreporter",
            kind="report",
            outcome="success",
            detail=f"{mode} for {result.window.start or 'all-time'} → {result.window.end}",
            window_start=result.window.start,
            window_end=result.window.end,
            entries_count=result.count,
            comment_url=comment_url,
            mode=mode,
        )
