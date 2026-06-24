from __future__ import annotations

from pathlib import Path

import pytest

from src import main


VALID_ESSAY = """# Technical Newsletter

Distributed system checkpointing creates measurable operational trade-offs at 99.9% availability targets.

| Prós | Contras | Decisão Técnica |
| :--- | :--- | :--- |
| Local writes complete in 10ms | Horizontal scale is limited | Use SQLiteSaver for isolated worker threads |

Official reference: https://www.sqlite.org/threadsafe.html.

""" + (" detailed architecture analysis" * 1000)


class FakeApp:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def invoke(self, state: dict[str, object], config: dict[str, object]) -> dict[str, object]:
        self.calls.append({"state": state, "config": config})
        return {
            "essay_draft": VALID_ESSAY,
            "validation_logs": [],
            "metadata": {"essay_word_count": len(VALID_ESSAY.split())},
        }


class FakeBridge:
    instances: list["FakeBridge"] = []

    def __init__(self, repo_path: str) -> None:
        self.repo_path = repo_path
        self.calls: list[str] = []
        self.saved_payload: dict[str, object] | None = None
        FakeBridge.instances.append(self)

    def initialize_workspace(self) -> None:
        self.calls.append("initialize_workspace")

    def save_edition(
        self,
        issue_id: str,
        slug: str,
        content: str,
        tokens_in: int,
        tokens_out: int,
        branch_name: str | None = None,
    ) -> dict[str, object]:
        self.calls.append("save_edition")
        self.saved_payload = {
            "issue_id": issue_id,
            "slug": slug,
            "content": content,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "branch_name": branch_name,
        }
        return {
            "md_path": str(Path(self.repo_path) / "content" / "editions" / "edition.md"),
            "meta_path": str(Path(self.repo_path) / "content" / "editions" / "edition.metadata.json"),
            "has_changed": True,
        }

    def checkout_issue_branch(self, issue_id: str) -> str:
        self.calls.append("checkout_issue_branch")
        return f"newsletter/issue-{issue_id.lower()}"

    def commit_and_push_edition(self, issue_id: str, slug: str, content: str, tokens_in: int, tokens_out: int) -> str:
        self.calls.append("commit_and_push_edition")
        self.saved_payload = {
            "issue_id": issue_id,
            "slug": slug,
            "content": content,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
        return "a" * 40


@pytest.fixture
def fake_runtime(monkeypatch):
    FakeBridge.instances = []
    app = FakeApp()
    monkeypatch.setattr(main, "compile_graph", lambda db_path: app)
    monkeypatch.setattr(main, "SymphonyGitBridge", FakeBridge)
    monkeypatch.setattr(main, "validate_essay_seniority", lambda essay: [])
    return app


def test_slugify_topic_handles_accents_and_spaces():
    assert main.slugify_topic("IA na Medicina") == "ia-na-medicina"
    assert main.slugify_topic("  ***  ") == "newsletter-edition"


def test_run_orchestration_dry_run_saves_without_push(fake_runtime, tmp_path):
    result = main.run_orchestration(
        topic="IA na Medicina",
        repo_path=tmp_path,
        db_path="content/test.db",
        issue_id="MEU-20",
        dry_run=True,
    )

    bridge = FakeBridge.instances[-1]
    assert bridge.calls == ["initialize_workspace", "save_edition"]
    assert result.status == "dry_run_saved"
    assert result.pushed is False
    assert result.slug == "ia-na-medicina"
    assert result.db_path == str(tmp_path / "content" / "test.db")
    assert bridge.saved_payload is not None
    assert bridge.saved_payload["tokens_in"] == 3
    assert bridge.saved_payload["tokens_out"] == len(VALID_ESSAY.split())


def test_run_orchestration_default_path_pushes_after_checkout(fake_runtime, tmp_path):
    result = main.run_orchestration(
        topic="LangGraph SQLite persistence",
        repo_path=tmp_path,
        issue_id="MEU-20",
    )

    bridge = FakeBridge.instances[-1]
    assert bridge.calls == ["initialize_workspace", "checkout_issue_branch", "commit_and_push_edition"]
    assert result.status == "pushed"
    assert result.pushed is True
    assert result.bridge_result == "a" * 40


def test_run_orchestration_raises_when_validator_rejects(monkeypatch, tmp_path):
    FakeBridge.instances = []
    monkeypatch.setattr(main, "compile_graph", lambda db_path: FakeApp())
    monkeypatch.setattr(main, "SymphonyGitBridge", FakeBridge)
    monkeypatch.setattr(main, "validate_essay_seniority", lambda essay: ["Word count (2) is below 1000 words."])

    with pytest.raises(main.OrchestrationValidationError) as exc_info:
        main.run_orchestration(topic="Too short", repo_path=tmp_path, dry_run=True)

    assert "Word count" in exc_info.value.errors[0]
