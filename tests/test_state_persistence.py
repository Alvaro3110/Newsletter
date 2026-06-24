import os
import sqlite3
import pytest
from src.core.graph import compile_graph
from src.core.state import NewsletterState

DB_PATH = "tests/test_newsletter_state.db"

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Ensure db directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    yield
    # Teardown: Clean up test db
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def test_graph_compilation_and_execution():
    """
    Validates that the graph compiles and executes successfully, saving state to SQLite.
    """
    app = compile_graph(DB_PATH)
    assert app is not None
    
    # Run the graph
    initial_state = {
        "topic_context": "Symphony Framework Persistence Layer Design",
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {}
    }
    
    config = {"configurable": {"thread_id": "thread-issue-17"}}
    
    # Execution
    final_output = app.invoke(initial_state, config=config)
    
    # Assertions
    assert "essay_draft" in final_output
    assert len(final_output["essay_draft"]) > 1000  # Enforce long-form
    assert len(final_output["research_sources"]) > 0
    assert len(final_output["analytical_points"]) > 0
    
    # Verify that the SQLite DB is created and has checkpoint data
    assert os.path.exists(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    assert "checkpoints" in tables
    
    # Check that we have a record for thread-issue-17
    cursor.execute("SELECT thread_id, checkpoint_id FROM checkpoints WHERE thread_id = ?;", ("thread-issue-17",))
    rows = cursor.fetchall()
    assert len(rows) > 0
    conn.close()

def test_graph_resume_from_checkpoint():
    """
    Validates that we can resume execution from a checkpoint or fetch current state.
    """
    app = compile_graph(DB_PATH)
    config = {"configurable": {"thread_id": "thread-issue-17-resume"}}
    
    initial_state = {
        "topic_context": "LangGraph Memory Savers",
        "research_sources": [],
        "analytical_points": [],
        "essay_draft": "",
        "validation_logs": [],
        "metadata": {}
    }
    
    # Run graph
    app.invoke(initial_state, config=config)
    
    # Get current state from database using checkpointer
    state_snapshot = app.get_state(config)
    assert state_snapshot is not None
    assert state_snapshot.values["topic_context"] == "LangGraph Memory Savers"
    assert "essay_draft" in state_snapshot.values
