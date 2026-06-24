from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from src.core.graph import compile_graph
from src.core.validator import validate_essay_seniority
from src.infra.workspace import SymphonyGitBridge

DEFAULT_DB_PATH = "content/newsletter_state.db"
DEFAULT_ISSUE_ID = "MEU-20"

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    status: str
    topic: str
    issue_id: str
    thread_id: str
    repo_path: str
    db_path: str
    slug: str
    word_count: int
    pushed: bool
    bridge_result: str
    edition_path: str | None
    metadata_path: str | None
    validation_logs: list[str]


class OrchestrationValidationError(RuntimeError):
    def __init__(self, errors: list[str]):
        super().__init__("Newsletter validation failed")
        self.errors = errors


def slugify_topic(topic: str) -> str:
    normalized = unicodedata.normalize("NFKD", topic)
    ascii_topic = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_topic.lower()).strip("-")
    return slug[:80] or "newsletter-edition"


def _resolve_repo_path(repo_path: str | Path) -> Path:
    return Path(repo_path).expanduser().resolve()


def _resolve_db_path(repo_path: Path, db_path: str | Path | None) -> Path:
    raw_path = Path(db_path or DEFAULT_DB_PATH).expanduser()
    if raw_path.is_absolute():
        return raw_path
    return repo_path / raw_path


def _initial_state(topic: str) -> dict[str, Any]:
    return {
        "topic_context": topic,
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {},
    }


def run_orchestration(
    *,
    topic: str,
    repo_path: str | Path = ".",
    db_path: str | Path | None = None,
    issue_id: str = DEFAULT_ISSUE_ID,
    thread_id: str | None = None,
    slug: str | None = None,
    dry_run: bool = False,
) -> OrchestrationResult:
    topic = topic.strip()
    if not topic:
        raise ValueError("Topic cannot be empty")

    resolved_repo_path = _resolve_repo_path(repo_path)
    resolved_db_path = _resolve_db_path(resolved_repo_path, db_path)
    resolved_thread_id = thread_id or f"thread-{issue_id.lower()}"
    resolved_slug = slug or slugify_topic(topic)

    bridge = SymphonyGitBridge(str(resolved_repo_path))
    bridge.initialize_workspace()

    app = compile_graph(str(resolved_db_path))
    final_state = app.invoke(_initial_state(topic), config={"configurable": {"thread_id": resolved_thread_id}})

    essay = final_state.get("essay_draft", "")
    if not essay:
        raise RuntimeError("Graph completed without producing essay_draft")

    validation_errors = validate_essay_seniority(essay)
    if validation_errors:
        raise OrchestrationValidationError(validation_errors)

    word_count = len(essay.split())
    tokens_in = len(topic.split())
    validation_logs = list(final_state.get("validation_logs", []))

    if dry_run:
        save_info = bridge.save_edition(
            issue_id=issue_id,
            slug=resolved_slug,
            content=essay,
            tokens_in=tokens_in,
            tokens_out=word_count,
        )
        return OrchestrationResult(
            status="dry_run_saved",
            topic=topic,
            issue_id=issue_id,
            thread_id=resolved_thread_id,
            repo_path=str(resolved_repo_path),
            db_path=str(resolved_db_path),
            slug=resolved_slug,
            word_count=word_count,
            pushed=False,
            bridge_result="Dry run saved edition; push skipped.",
            edition_path=str(save_info["md_path"]),
            metadata_path=str(save_info["meta_path"]),
            validation_logs=validation_logs,
        )

    bridge.checkout_issue_branch(issue_id)
    commit_sha = bridge.commit_and_push_edition(
        issue_id=issue_id,
        slug=resolved_slug,
        content=essay,
        tokens_in=tokens_in,
        tokens_out=word_count,
    )
    return OrchestrationResult(
        status="pushed",
        topic=topic,
        issue_id=issue_id,
        thread_id=resolved_thread_id,
        repo_path=str(resolved_repo_path),
        db_path=str(resolved_db_path),
        slug=resolved_slug,
        word_count=word_count,
        pushed=True,
        bridge_result=commit_sha,
        edition_path=None,
        metadata_path=None,
        validation_logs=validation_logs,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the newsletter orchestration flow from START to PUSH.")
    parser.add_argument("--topic", required=True, help='Newsletter topic, for example: "IA na Medicina".')
    parser.add_argument("--issue-id", default=DEFAULT_ISSUE_ID, help=f"Linear issue id for generated metadata. Defaults to {DEFAULT_ISSUE_ID}.")
    parser.add_argument("--repo-path", default=".", help="Git repository path used by the workspace bridge.")
    parser.add_argument("--db-path", default=None, help=f"SQLite checkpoint path. Defaults to {DEFAULT_DB_PATH} under repo path.")
    parser.add_argument("--thread-id", default=None, help="LangGraph checkpoint thread id. Defaults to thread-<issue-id>.")
    parser.add_argument("--slug", default=None, help="Edition slug. Defaults to a slug derived from --topic.")
    parser.add_argument("--dry-run", action="store_true", help="Run START through validation and save files without committing or pushing.")
    parser.add_argument("--verbose", action="store_true", help="Enable info-level orchestration logs.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    try:
        result = run_orchestration(
            topic=args.topic,
            repo_path=args.repo_path,
            db_path=args.db_path,
            issue_id=args.issue_id,
            thread_id=args.thread_id,
            slug=args.slug,
            dry_run=args.dry_run,
        )
    except OrchestrationValidationError as exc:
        print(json.dumps({"status": "validation_failed", "errors": exc.errors}, indent=2), file=sys.stderr)
        return 2
    except Exception as exc:
        logger.exception("Orchestration failed")
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
