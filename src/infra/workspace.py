import json
import os
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict


class SymphonyGitBridge:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.content_dir = os.path.join(repo_path, "content")
        self.editions_dir = os.path.join(self.content_dir, "editions")
        self.assets_dir = os.path.join(self.content_dir, "assets", "images")

    def initialize_workspace(self) -> None:
        """
        Creates the standard directory structure in the repository.
        """
        os.makedirs(self.editions_dir, exist_ok=True)
        os.makedirs(self.assets_dir, exist_ok=True)

    def run_git_command(self, args: list[str]) -> str:
        """
        Runs a git command in the repository path.
        """
        result = subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def checkout_issue_branch(self, issue_id: str) -> str:
        """
        Creates and/or checkouts a branch for the given issue.
        """
        branch_name = f"newsletter/issue-{issue_id.lower()}"
        try:
            self.run_git_command(["checkout", branch_name])
        except subprocess.CalledProcessError:
            self.run_git_command(["checkout", "-b", branch_name])
        return branch_name

    def _edition_digest(self, issue_id: str, slug: str, content: str, tokens_in: int, tokens_out: int) -> str:
        payload = json.dumps(
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
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def save_edition(
        self,
        issue_id: str,
        slug: str,
        content: str,
        tokens_in: int,
        tokens_out: int,
        branch_name: str | None = None,
    ) -> Dict[str, Any]:
        """
        Saves the markdown edition and metadata.json.
        Returns a dict containing the file paths and whether changes were detected.
        """
        self.initialize_workspace()

        now = datetime.now(timezone.utc)
        year = now.strftime("%Y")
        month_day = now.strftime("%m-%d")
        edition_digest = self._edition_digest(issue_id, slug, content, tokens_in, tokens_out)

        target_dir = os.path.join(self.editions_dir, year)
        os.makedirs(target_dir, exist_ok=True)

        md_filename = f"{month_day}-{slug}.md"
        meta_filename = f"{month_day}-{slug}.metadata.json"

        md_path = os.path.join(target_dir, md_filename)
        meta_path = os.path.join(target_dir, meta_filename)

        has_changed = True
        if os.path.exists(md_path) and os.path.exists(meta_path):
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    existing_md = f.read()
                with open(meta_path, "r", encoding="utf-8") as f:
                    existing_meta = json.load(f)

                if (
                    existing_md == content
                    and existing_meta.get("linear_issue_id") == issue_id
                    and existing_meta.get("tokens_consumed_in") == tokens_in
                    and existing_meta.get("tokens_consumed_out") == tokens_out
                    and existing_meta.get("edition_digest") == edition_digest
                ):
                    has_changed = False
            except Exception:
                has_changed = True

        if has_changed:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)

            meta_data = {
                "linear_issue_id": issue_id,
                "generation_timestamp": now.isoformat() + "Z",
                "tokens_consumed_in": tokens_in,
                "tokens_consumed_out": tokens_out,
                "edition_digest": edition_digest,
                "git_branch": branch_name or "",
            }

            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_data, f, indent=2)

        return {
            "md_path": md_path,
            "meta_path": meta_path,
            "has_changed": has_changed,
            "edition_digest": edition_digest,
        }

    def commit_and_push_edition(self, issue_id: str, slug: str, content: str, tokens_in: int, tokens_out: int) -> str:
        """
        Saves, commits with the standardized message and Linear issue link, and pushes to remote.
        """
        branch_name = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        save_info = self.save_edition(issue_id, slug, content, tokens_in, tokens_out, branch_name=branch_name)

        if not save_info["has_changed"]:
            status = self.run_git_command(["status", "--porcelain"])
            if not status:
                return "No changes detected. Skip commit."

        rel_md_path = os.path.relpath(save_info["md_path"], self.repo_path)
        rel_meta_path = os.path.relpath(save_info["meta_path"], self.repo_path)

        self.run_git_command(["add", rel_md_path, rel_meta_path])

        commit_message = f"feat: edition for {issue_id}\n\nLinear Issue: https://linear.app/issue/{issue_id}"
        self.run_git_command(["commit", "-m", commit_message])

        commit_sha = self.run_git_command(["rev-parse", "HEAD"])
        self.run_git_command(["push", "-u", "origin", branch_name])

        return commit_sha
