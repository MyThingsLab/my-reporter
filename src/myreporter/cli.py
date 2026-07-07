from __future__ import annotations

import argparse
from pathlib import Path

from mythings.engine import ClaudeCLIEngine, Engine, NoopEngine

from myreporter.reporter import Reporter

_ENGINES: dict[str, type[Engine]] = {"noop": NoopEngine, "claude-cli": ClaudeCLIEngine}


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--since", help="ISO8601 window start (default: since the last report)")
    parser.add_argument("--repo", help="GitHub slug owner/name")
    parser.add_argument("--ledger", type=Path, default=Path(".mythings/ledger.jsonl"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--handoff",
        action="store_true",
        help="render a resume-context brief (open threads, decisions, last ship) "
        "instead of the aggregate digest",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="myreporter",
        description="Digest the Ledger + dev-ledger and print or post it.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    digest = sub.add_parser("digest", help="print the markdown digest to stdout")
    _add_common(digest)

    post = sub.add_parser("post", help="comment the digest on an issue")
    _add_common(post)
    post.add_argument("--issue", type=int, required=True)
    post.add_argument("--summarize", action="store_true", help="append an Engine prose summary")
    post.add_argument(
        "--engine",
        choices=sorted(_ENGINES),
        default="noop",
        help="Engine backend for --summarize (default: noop — no tokens spent, "
        "no-op unless --summarize is also passed)",
    )

    args = parser.parse_args(argv)
    engine = _ENGINES[args.engine]() if args.cmd == "post" else None
    reporter = Reporter(
        ledger_path=args.ledger, repo_root=args.repo_root, repo=args.repo, engine=engine
    )

    if args.cmd == "digest":
        print(reporter.digest(since=args.since, handoff=args.handoff).markdown)
        return 0

    result = reporter.post(
        args.issue, since=args.since, summarize=args.summarize, handoff=args.handoff
    )
    mode = "handoff" if args.handoff else "digest"
    print(f"posted {mode} ({result.count} entries) to {args.repo}#{args.issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
