import requests
from typing import Optional


class GitHubService:
    """Service class for all GitHub REST API operations."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def _get(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make authenticated GET request to GitHub API."""
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                remaining = response.headers.get("X-RateLimit-Remaining", "0")
                if remaining == "0":
                    reset_time = response.headers.get("X-RateLimit-Reset", "")
                    return {"error": f"Rate limit exceeded. Resets at: {reset_time}"}
            elif response.status_code == 404:
                return {"error": "Resource not found"}
            return {"error": f"API error {response.status_code}"}
        except requests.RequestException as e:
            return {"error": str(e)}

    def _post(self, endpoint: str, data: dict) -> Optional[dict]:
        """Make authenticated POST request to GitHub API."""
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.post(url, json=data, timeout=15)
            if response.status_code in (200, 201):
                return response.json()
            return {"error": f"API error {response.status_code}: {response.text}"}
        except requests.RequestException as e:
            return {"error": str(e)}

    # ─── Repository ───────────────────────────────────────────────────────────

    def get_repository(self, owner: str, repo: str) -> dict:
        return self._get(f"/repos/{owner}/{repo}")

    def get_branches(self, owner: str, repo: str) -> list:
        result = self._get(f"/repos/{owner}/{repo}/branches", params={"per_page": 50})
        return result if isinstance(result, list) else []

    def get_commits(self, owner: str, repo: str, per_page: int = 20) -> list:
        result = self._get(f"/repos/{owner}/{repo}/commits", params={"per_page": per_page})
        return result if isinstance(result, list) else []

    def get_contributors(self, owner: str, repo: str) -> list:
        result = self._get(f"/repos/{owner}/{repo}/contributors", params={"per_page": 30})
        return result if isinstance(result, list) else []

    def get_languages(self, owner: str, repo: str) -> dict:
        result = self._get(f"/repos/{owner}/{repo}/languages")
        return result if isinstance(result, dict) and "error" not in result else {}

    # ─── Issues ───────────────────────────────────────────────────────────────

    def get_issues(self, owner: str, repo: str, state: str = "all", per_page: int = 50) -> list:
        result = self._get(f"/repos/{owner}/{repo}/issues",
                           params={"state": state, "per_page": per_page, "sort": "updated"})
        if isinstance(result, list):
            # Filter out PRs (GitHub API returns PRs as issues too)
            return [i for i in result if "pull_request" not in i]
        return []

    def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                     labels: list = None, assignees: list = None) -> dict:
        data = {"title": title, "body": body}
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        return self._post(f"/repos/{owner}/{repo}/issues", data)

    def get_labels(self, owner: str, repo: str) -> list:
        result = self._get(f"/repos/{owner}/{repo}/labels", params={"per_page": 50})
        return result if isinstance(result, list) else []

    # ─── Pull Requests ────────────────────────────────────────────────────────

    def get_pull_requests(self, owner: str, repo: str, state: str = "all", per_page: int = 30) -> list:
        result = self._get(f"/repos/{owner}/{repo}/pulls",
                           params={"state": state, "per_page": per_page, "sort": "updated"})
        return result if isinstance(result, list) else []

    def get_pr_reviews(self, owner: str, repo: str, pull_number: int) -> list:
        result = self._get(f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews")
        return result if isinstance(result, list) else []

    def get_pr_checks(self, owner: str, repo: str, ref: str) -> dict:
        return self._get(f"/repos/{owner}/{repo}/commits/{ref}/check-runs")

    # ─── Milestones ───────────────────────────────────────────────────────────

    def get_milestones(self, owner: str, repo: str, state: str = "all") -> list:
        result = self._get(f"/repos/{owner}/{repo}/milestones",
                           params={"state": state, "per_page": 30})
        return result if isinstance(result, list) else []

    def create_milestone(self, owner: str, repo: str, title: str, due_on: str = None,
                          description: str = "") -> dict:
        data = {"title": title, "description": description}
        if due_on:
            data["due_on"] = due_on
        return self._post(f"/repos/{owner}/{repo}/milestones", data)

    # ─── GitHub Actions / Workflows ───────────────────────────────────────────

    def get_workflows(self, owner: str, repo: str) -> dict:
        return self._get(f"/repos/{owner}/{repo}/actions/workflows")

    def get_workflow_runs(self, owner: str, repo: str, per_page: int = 20) -> dict:
        return self._get(f"/repos/{owner}/{repo}/actions/runs",
                         params={"per_page": per_page})

    def get_workflow_run_jobs(self, owner: str, repo: str, run_id: int) -> dict:
        return self._get(f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs")

    def get_check_runs_for_commit(self, owner: str, repo: str, sha: str) -> dict:
        return self._get(f"/repos/{owner}/{repo}/commits/{sha}/check-runs")

    # ─── Repository Stats ─────────────────────────────────────────────────────

    def get_repository_stats(self, owner: str, repo: str) -> dict:
        """Aggregate repository statistics."""
        repo_data = self.get_repository(owner, repo)
        if not repo_data or "error" in repo_data:
            return {"error": "Could not fetch repository"}

        open_issues = self.get_issues(owner, repo, state="open")
        closed_issues = self.get_issues(owner, repo, state="closed")
        open_prs = self.get_pull_requests(owner, repo, state="open")
        closed_prs = self.get_pull_requests(owner, repo, state="closed")

        merged_prs = [pr for pr in closed_prs if pr.get("merged_at")]
        commits = self.get_commits(owner, repo, per_page=10)
        branches = self.get_branches(owner, repo)
        languages = self.get_languages(owner, repo)

        return {
            "repository": repo_data,
            "stats": {
                "open_issues": len(open_issues),
                "closed_issues": len(closed_issues),
                "total_issues": len(open_issues) + len(closed_issues),
                "open_prs": len(open_prs),
                "merged_prs": len(merged_prs),
                "total_prs": len(open_prs) + len(closed_prs),
                "branches": len(branches),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "default_branch": repo_data.get("default_branch", "main"),
            },
            "recent_commits": commits[:5],
            "branches": branches,
            "languages": languages,
        }

    # ─── Simulated Data (fallback when no token) ──────────────────────────────

    @staticmethod
    def get_demo_data() -> dict:
        """Return realistic demo data for presentation / offline mode."""
        return {
            "repository": {
                "name": "online-exam-system",
                "full_name": "teamsync-demo/online-exam-system",
                "description": "AI-based Online Examination System built with Python & Flask",
                "default_branch": "main",
                "language": "Python",
                "stargazers_count": 12,
                "forks_count": 3,
                "open_issues_count": 8,
                "html_url": "https://github.com/teamsync-demo/online-exam-system",
                "created_at": "2024-10-01T00:00:00Z",
                "pushed_at": "2024-11-28T14:30:00Z",
                "private": False,
            },
            "stats": {
                "open_issues": 8,
                "closed_issues": 22,
                "total_issues": 30,
                "open_prs": 4,
                "merged_prs": 14,
                "total_prs": 18,
                "branches": 7,
                "stars": 12,
                "forks": 3,
                "watchers": 8,
                "default_branch": "main",
            },
            "recent_commits": [
                {"sha": "a1b2c3d", "commit": {"message": "feat: Add JWT authentication", "author": {"name": "Alice Dev", "date": "2024-11-28T14:00:00Z"}}},
                {"sha": "e4f5g6h", "commit": {"message": "fix: Resolve session timeout bug", "author": {"name": "Bob Coder", "date": "2024-11-28T10:00:00Z"}}},
                {"sha": "i7j8k9l", "commit": {"message": "test: Add Pytest coverage for exam module", "author": {"name": "Carol QA", "date": "2024-11-27T16:30:00Z"}}},
                {"sha": "m1n2o3p", "commit": {"message": "ci: Update GitHub Actions workflow", "author": {"name": "David DevOps", "date": "2024-11-27T09:00:00Z"}}},
                {"sha": "q4r5s6t", "commit": {"message": "docs: Update README with setup guide", "author": {"name": "Eve Docs", "date": "2024-11-26T17:00:00Z"}}},
            ],
            "branches": [
                {"name": "main", "protected": True},
                {"name": "develop", "protected": False},
                {"name": "feature/authentication", "protected": False},
                {"name": "feature/exam-module", "protected": False},
                {"name": "feature/result-generation", "protected": False},
                {"name": "bugfix/login-session", "protected": False},
                {"name": "release/v1.0.0", "protected": True},
            ],
            "languages": {"Python": 68420, "HTML": 12300, "CSS": 4100, "JavaScript": 2800},
        }
