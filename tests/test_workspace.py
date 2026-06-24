import os
import json
import shutil
import tempfile
import subprocess
import pytest
from src.infra.workspace import SymphonyGitBridge

@pytest.fixture
def temp_git_workspace():
    # Setup temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Setup a local bare repository to act as origin remote
    remote_dir = tempfile.mkdtemp()
    subprocess.run(["git", "init", "--bare"], cwd=remote_dir, check=True)
    
    # Setup the working repository
    repo_dir = os.path.join(temp_dir, "newsletter_repo")
    os.makedirs(repo_dir)
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@newsletter.com"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    
    # Create initial commit
    readme_path = os.path.join(repo_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("# Newsletter Test")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_dir, check=True)
    
    # Link remote origin
    subprocess.run(["git", "remote", "add", "origin", remote_dir], cwd=repo_dir, check=True)
    # Set default branch
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_dir, check=True)
    # Push main branch
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_dir, check=True)
    
    yield repo_dir
    
    # Teardown
    shutil.rmtree(temp_dir)
    shutil.rmtree(remote_dir)

def test_workspace_initialization_and_commit(temp_git_workspace):
    bridge = SymphonyGitBridge(temp_git_workspace)
    bridge.initialize_workspace()
    
    # Check directory structure
    assert os.path.exists(bridge.editions_dir)
    assert os.path.exists(bridge.assets_dir)
    
    # Checkout branch
    branch_name = bridge.checkout_issue_branch("MEU-18")
    assert branch_name == "newsletter/issue-meu-18"
    
    # Save edition and commit
    issue_id = "MEU-18"
    slug = "checkpointing-resiliente"
    content = "# Resiliência no LangGraph\nArtigo sobre SqliteSaver."
    tokens_in = 500
    tokens_out = 1500
    
    commit_sha = bridge.commit_and_push_edition(
        issue_id=issue_id,
        slug=slug,
        content=content,
        tokens_in=tokens_in,
        tokens_out=tokens_out
    )
    
    assert len(commit_sha) == 40  # Valid Git commit SHA length
    
    # Check that MD and metadata exist
    now_year = datetime_year = os.listdir(bridge.editions_dir)[0]
    edition_year_dir = os.path.join(bridge.editions_dir, now_year)
    files = os.listdir(edition_year_dir)
    
    md_file = [f for f in files if f.endswith(".md")][0]
    meta_file = [f for f in files if f.endswith(".json")][0]
    
    # Check MD content
    with open(os.path.join(edition_year_dir, md_file), "r") as f:
        md_content = f.read()
    assert md_content == content
    
    # Check Metadata JSON content
    with open(os.path.join(edition_year_dir, meta_file), "r") as f:
        meta_content = json.load(f)
        
    assert meta_content["linear_issue_id"] == issue_id
    assert meta_content["tokens_consumed_in"] == tokens_in
    assert meta_content["tokens_consumed_out"] == tokens_out
    assert meta_content["git_commit_sha"] == commit_sha
    
    # Check git log commit message contains linear link
    log = bridge.run_git_command(["log", "-n", "1"])
    assert f"feat: edition for {issue_id}" in log
    assert f"https://linear.app/issue/{issue_id}" in log

def test_prevent_duplicate_commit(temp_git_workspace):
    bridge = SymphonyGitBridge(temp_git_workspace)
    bridge.initialize_workspace()
    
    bridge.checkout_issue_branch("MEU-18")
    
    issue_id = "MEU-18"
    slug = "checkpointing-resiliente"
    content = "# Resiliência no LangGraph\nArtigo sobre SqliteSaver."
    
    # First commit
    sha1 = bridge.commit_and_push_edition(issue_id, slug, content, 100, 200)
    assert len(sha1) == 40
    
    # Second run without changes should return skip message
    result = bridge.commit_and_push_edition(issue_id, slug, content, 100, 200)
    assert result == "No changes detected. Skip commit."
