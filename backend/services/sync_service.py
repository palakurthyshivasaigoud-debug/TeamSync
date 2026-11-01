import json
import hmac
import hashlib
from datetime import datetime
from flask import current_app
from ..models import WebhookEvent, Issue, PullRequest, Project
from ..extensions import db


class SyncService:
    """Process GitHub webhook events and keep the local database in sync."""

    def verify_signature(self, payload_body: bytes, signature: str) -> bool:
        """Verify X-Hub-Signature-256 header."""
        secret = current_app.config.get("GITHUB_WEBHOOK_SECRET", "").encode()
        expected = "sha256=" + hmac.new(secret, payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature or "")

    def handle_event(self, delivery_id: str, event_type: str, payload: dict) -> dict:
        """Route webhook event to appropriate handler."""
        # Idempotency check
        existing = WebhookEvent.query.filter_by(delivery_id=delivery_id).first()
        if existing and existing.processed:
            return {"status": "duplicate", "delivery_id": delivery_id}

        webhook = WebhookEvent(
            delivery_id=delivery_id,
            event_type=event_type,
            repository=payload.get("repository", {}).get("full_name"),
            payload=json.dumps(payload),
            processed=False,
        )
        db.session.add(webhook)
        db.session.flush()

        try:
            handlers = {
                "issues": self._handle_issues,
                "pull_request": self._handle_pull_request,
                "pull_request_review": self._handle_pr_review,
                "push": self._handle_push,
                "check_run": self._handle_check_run,
                "workflow_run": self._handle_workflow_run,
                "milestone": self._handle_milestone,
            }
            handler = handlers.get(event_type)
            if handler:
                handler(payload)

            webhook.processed = True
            db.session.commit()
            return {"status": "processed", "event": event_type}

        except Exception as e:
            webhook.error_message = str(e)
            db.session.commit()
            return {"status": "error", "message": str(e)}

    def _find_project(self, payload: dict):
        repo = payload.get("repository", {})
        owner = repo.get("owner", {}).get("login", "")
        name = repo.get("name", "")
        return Project.query.filter_by(
            repository_owner=owner, repository_name=name
        ).first()

    def _handle_issues(self, payload: dict):
        project = self._find_project(payload)
        if not project:
            return
        action = payload.get("action")
        gh_issue = payload.get("issue", {})
        issue_number = gh_issue.get("number")

        issue = Issue.query.filter_by(
            project_id=project.id,
            github_issue_number=issue_number
        ).first()

        labels_raw = gh_issue.get("labels", [])
        labels_str = ",".join(l["name"] for l in labels_raw)
        is_bug = any(l["name"].lower() in ("bug", "defect", "error") for l in labels_raw)

        if not issue:
            issue = Issue(project_id=project.id, github_issue_number=issue_number)
            db.session.add(issue)

        issue.title = gh_issue.get("title", "")
        issue.body = gh_issue.get("body", "")
        issue.state = gh_issue.get("state", "open")
        issue.labels = labels_str
        issue.is_bug = is_bug
        issue.assignee = (gh_issue.get("assignee") or {}).get("login")
        issue.author = (gh_issue.get("user") or {}).get("login")
        issue.github_url = gh_issue.get("html_url", "")
        issue.updated_at = datetime.utcnow()

    def _handle_pull_request(self, payload: dict):
        project = self._find_project(payload)
        if not project:
            return
        action = payload.get("action")
        gh_pr = payload.get("pull_request", {})
        pr_number = gh_pr.get("number")

        pr = PullRequest.query.filter_by(
            project_id=project.id,
            github_pr_number=pr_number
        ).first()
        if not pr:
            pr = PullRequest(project_id=project.id, github_pr_number=pr_number)
            db.session.add(pr)

        pr.title = gh_pr.get("title", "")
        pr.author = (gh_pr.get("user") or {}).get("login")
        pr.state = gh_pr.get("state", "open")
        pr.merged = gh_pr.get("merged", False)
        pr.draft = gh_pr.get("draft", False)
        pr.head_branch = (gh_pr.get("head") or {}).get("ref")
        pr.base_branch = (gh_pr.get("base") or {}).get("ref", "main")
        pr.changed_files = gh_pr.get("changed_files", 0)
        pr.additions = gh_pr.get("additions", 0)
        pr.deletions = gh_pr.get("deletions", 0)
        pr.github_url = gh_pr.get("html_url", "")
        pr.updated_at = datetime.utcnow()
        if gh_pr.get("merged_at"):
            pr.merged_at = datetime.fromisoformat(gh_pr["merged_at"].replace("Z", "+00:00"))

    def _handle_pr_review(self, payload: dict):
        project = self._find_project(payload)
        if not project:
            return
        gh_pr = payload.get("pull_request", {})
        review = payload.get("review", {})
        pr_number = gh_pr.get("number")

        pr = PullRequest.query.filter_by(
            project_id=project.id,
            github_pr_number=pr_number
        ).first()
        if pr:
            state = review.get("state", "").lower()
            if state == "approved":
                pr.review_status = "approved"
            elif state == "changes_requested":
                pr.review_status = "changes_requested"

    def _handle_push(self, payload: dict):
        # Push events are logged; could trigger sync in future
        pass

    def _handle_check_run(self, payload: dict):
        project = self._find_project(payload)
        if not project:
            return
        check = payload.get("check_run", {})
        conclusion = check.get("conclusion")
        if conclusion in ("success", "neutral"):
            status = "passed"
        elif conclusion in ("failure", "timed_out", "action_required"):
            status = "failed"
        else:
            status = "pending"

        # Update PR check status
        pr_numbers = [pr["number"] for pr in check.get("pull_requests", [])]
        for pr_number in pr_numbers:
            pr = PullRequest.query.filter_by(
                project_id=project.id,
                github_pr_number=pr_number
            ).first()
            if pr:
                pr.check_status = status

    def _handle_workflow_run(self, payload: dict):
        # Workflow run results logged for quality reports
        pass

    def _handle_milestone(self, payload: dict):
        pass
