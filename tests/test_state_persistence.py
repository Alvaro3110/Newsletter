
import os
import sqlite3
from pathlib import Path

import pytest

from src.core.graph import compile_graph, research_node
from src.core.validator import validate_essay_seniority


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_newsletter_state.db"


def test_graph_compilation_and_execution(db_path: Path):
    """
    Validates that the graph compiles and executes successfully, saving state to SQLite.
    """
    app = compile_graph(str(db_path))
    assert app is not None

    initial_state = {
        "topic_context": "Symphony Framework Persistence Layer Design",
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {},
    }

    config = {"configurable": {"thread_id": "thread-issue-17"}}
    final_output = app.invoke(initial_state, config=config)

    assert "essay_draft" in final_output
    assert len(final_output["essay_draft"].split()) >= 1000
    assert validate_essay_seniority(final_output["essay_draft"]) == []
    assert len(final_output["research_sources"]) > 0
    assert len(final_output["analytical_points"]) > 0
    assert final_output["metadata"]["research_metadata"]["research_mode"] == "internal_fallback"

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    assert "checkpoints" in tables

    cursor.execute("SELECT thread_id, checkpoint_id FROM checkpoints WHERE thread_id = ?;", ("thread-issue-17",))
    rows = cursor.fetchall()
    assert len(rows) > 0
    conn.close()


def test_graph_creates_parent_directory_for_database(tmp_path: Path):
    nested_db = tmp_path / "nested" / "newsletter_state.db"

    app = compile_graph(str(nested_db))
    assert app is not None
    assert nested_db.parent.exists()


def test_graph_resume_from_checkpoint(db_path: Path):
    """
    Validates that we can resume execution from a checkpoint or fetch current state.
    """
    app = compile_graph(str(db_path))
    config = {"configurable": {"thread_id": "thread-issue-17-resume"}}

    initial_state = {
        "topic_context": "LangGraph Memory Savers",
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {},
    }

    app.invoke(initial_state, config=config)

    state_snapshot = app.get_state(config)
    assert state_snapshot is not None
    assert state_snapshot.values["topic_context"] == "LangGraph Memory Savers"
    assert "essay_draft" in state_snapshot.values


def test_research_node_marks_internal_fallback_when_search_is_unavailable(monkeypatch):
    monkeypatch.delenv("RESEARCH_API_URL", raising=False)

    result = research_node({
        "topic_context": "Checkpointing in long-lived agents",
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {},
    })

    assert result["metadata"]["research_metadata"]["research_mode"] == "internal_fallback"
    assert result["metadata"]["research_metadata"]["research_stale"] is True
    assert len(result["research_sources"]) > 0
