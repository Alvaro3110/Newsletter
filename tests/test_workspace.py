import hashlib
import json
import os
import shutil
import subprocess
import tempfile

import pytest

from src.infra.workspace import SymphonyGitBridge


@pytest.fixture
def temp_git_workspace():
    temp_dir = tempfile.mkdtemp()

    remote_dir = tempfile.mkdtemp()
    subprocess.run(["git", "init", "--bare"], cwd=remote_dir, check=True)

    repo_dir = os.path.join(temp_dir, "newsletter_repo")
    os.makedirs(repo_dir)
    subprocess.run(["git", "init"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@newsletter.com"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)

    readme_path = os.path.join(repo_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Newsletter Test")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_dir, check=True)

    subprocess.run(["git", "remote", "add", "origin", remote_dir], cwd=repo_dir, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_dir, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_dir, check=True)

    yield repo_dir

    shutil.rmtree(temp_dir)
    shutil.rmtree(remote_dir)


def test_workspace_initialization_and_commit(temp_git_workspace):
    bridge = SymphonyGitBridge(temp_git_workspace)
    bridge.initialize_workspace()

    assert os.path.exists(bridge.editions_dir)
    assert os.path.exists(bridge.assets_dir)

    branch_name = bridge.checkout_issue_branch("MEU-18")
    assert branch_name == "newsletter/issue-meu-18"

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
        tokens_out=tokens_out,
    )

    assert len(commit_sha) == 40

    now_year = os.listdir(bridge.editions_dir)[0]
    edition_year_dir = os.path.join(bridge.editions_dir, now_year)
    files = os.listdir(edition_year_dir)

    md_file = [f for f in files if f.endswith(".md")][0]
    meta_file = [f for f in files if f.endswith(".json")][0]

    with open(os.path.join(edition_year_dir, md_file), "r", encoding="utf-8") as f:
        md_content = f.read()
    assert md_content == content

    with open(os.path.join(edition_year_dir, meta_file), "r", encoding="utf-8") as f:
        meta_content = json.load(f)

    expected_digest = hashlib.sha256(
        json.dumps(
            {
                "issue_id": issue_id,
                "slug": slug,
                "content": content,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    assert meta_content["linear_issue_id"] == issue_id
    assert meta_content["tokens_consumed_in"] == tokens_in
    assert meta_content["tokens_consumed_out"] == tokens_out
    assert meta_content["edition_digest"] == expected_digest
    assert meta_content["git_branch"] == "newsletter/issue-meu-18"
    assert "git_commit_sha" not in meta_content

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

    sha1 = bridge.commit_and_push_edition(issue_id, slug, content, 100, 200)
    assert len(sha1) == 40

    result = bridge.commit_and_push_edition(issue_id, slug, content, 100, 200)
    assert result == "No changes detected. Skip commit."
