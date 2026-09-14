from __future__ import annotations

import argparse
from pathlib import Path

from mythings.engine import build_engine_from_args

from myreporter.reporter import Reporter

_ENGINE_NAMES = ("noop", "claude-cli")


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
    digest.add_argument(
        "--quiet-if-clean",
        action="store_true",
        help="with --handoff: print nothing and exit 2 instead of a "
        "'clean baseline' placeholder (for a caller concatenating many repos)",
    )

    post = sub.add_parser("post", help="comment the digest on an issue")
    _add_common(post)
    post.add_argument("--issue", type=int, required=True)
    post.add_argument("--summarize", action="store_true", help="append an Engine prose summary")
    post.add_argument(
        "--engine",
        choices=sorted(_ENGINE_NAMES),
        default="noop",
        help="Engine backend for --summarize (default: noop — no tokens spent, "
        "no-op unless --summarize is also passed)",
    )
    post.add_argument(
        "--engine-model",
        help="model for --engine claude-cli (default: the CLI's own default; "
        "ignored by noop)",
    )

    args = parser.parse_args(argv)
    engine = build_engine_from_args(args) if args.cmd == "post" else None
    reporter = Reporter(
        ledger_path=args.ledger, repo_root=args.repo_root, repo=args.repo, engine=engine
    )

    if args.cmd == "digest":
        result = reporter.digest(since=args.since, handoff=args.handoff)
        if args.quiet_if_clean and not result.has_content:
            return 2
        print(result.markdown)
        return 0

    result = reporter.post(
        args.issue, since=args.since, summarize=args.summarize, handoff=args.handoff
    )
    mode = "handoff" if args.handoff else "digest"
    print(f"posted {mode} ({result.count} entries) to {args.repo}#{args.issue}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
