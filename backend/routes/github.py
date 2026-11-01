from flask import Blueprint, request, jsonify, current_app
from ..services.github_service import GitHubService
from ..models import Project, Issue, PullRequest
from ..extensions import db

github_bp = Blueprint("github", __name__)


def _get_service() -> GitHubService:
    token = current_app.config.get("GITHUB_TOKEN", "")
    return GitHubService(token)


@github_bp.route("/repo", methods=["GET"])
def get_repo():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    if not owner or not repo:
        # Return demo data
        return jsonify(GitHubService.get_demo_data())
    svc = _get_service()
    return jsonify(svc.get_repository_stats(owner, repo))


@github_bp.route("/branches", methods=["GET"])
def get_branches():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    if not owner or not repo:
        demo = GitHubService.get_demo_data()
        return jsonify(demo["branches"])
    svc = _get_service()
    return jsonify(svc.get_branches(owner, repo))


@github_bp.route("/commits", methods=["GET"])
def get_commits():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    per_page = request.args.get("per_page", 20, type=int)
    if not owner or not repo:
        demo = GitHubService.get_demo_data()
        return jsonify(demo["recent_commits"])
    svc = _get_service()
    return jsonify(svc.get_commits(owner, repo, per_page))


@github_bp.route("/issues", methods=["GET"])
def get_issues():
    project_id = request.args.get("project_id", type=int)
    if project_id:
        project = Project.query.get(project_id)
        issues = project.issues if project else []
        return jsonify([i.to_dict() for i in issues])
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    state = request.args.get("state", "all")
    if not owner or not repo:
        return jsonify([])
    svc = _get_service()
    return jsonify(svc.get_issues(owner, repo, state))


@github_bp.route("/issues", methods=["POST"])
def create_issue():
    data = request.get_json() or {}
    project_id = data.get("project_id", 1)
    title = data.get("title")
    if not title:
        return jsonify({"error": "Title required"}), 400
    
    max_num = db.session.query(db.func.max(Issue.github_issue_number)).filter_by(project_id=project_id).scalar() or 8
    is_bug = data.get("is_bug", False)
    labels = data.get("labels", "enhancement" if not is_bug else "bug")
    
    issue = Issue(
        project_id=project_id,
        github_issue_number=max_num + 1,
        title=title,
        body=data.get("body", ""),
        state="open",
        labels=labels,
        assignee=data.get("assignee", "arjun-mehta"),
        author=data.get("author", "priya-sharma"),
        is_bug=is_bug,
        github_url=f"https://github.com/teamsync-demo/online-exam-system/issues/{max_num + 1}",
    )
    db.session.add(issue)
    db.session.commit()
    return jsonify(issue.to_dict()), 201


@github_bp.route("/pull-requests", methods=["GET"])
def get_pull_requests():
    project_id = request.args.get("project_id", type=int)
    if project_id:
        project = Project.query.get(project_id)
        prs = project.pull_requests if project else []
        return jsonify([pr.to_dict() for pr in prs])
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    state = request.args.get("state", "all")
    if not owner or not repo:
        return jsonify([])
    svc = _get_service()
    return jsonify(svc.get_pull_requests(owner, repo, state))


@github_bp.route("/workflows", methods=["GET"])
def get_workflows():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    if not owner or not repo:
        return jsonify(_demo_workflow_data())
    svc = _get_service()
    data = svc.get_workflows(owner, repo)
    return jsonify(data if data else _demo_workflow_data())


@github_bp.route("/workflow-runs", methods=["GET"])
def get_workflow_runs():
    owner = request.args.get("owner")
    repo = request.args.get("repo")
    if not owner or not repo:
        return jsonify(_demo_workflow_runs())
    svc = _get_service()
    data = svc.get_workflow_runs(owner, repo)
    return jsonify(data if data else _demo_workflow_runs())


@github_bp.route("/milestones", methods=["GET"])
def get_milestones():
    project_id = request.args.get("project_id", type=int)
    if project_id:
        project = Project.query.get(project_id)
        ms = project.milestones if project else []
        return jsonify([m.to_dict() for m in ms])
    return jsonify([])


@github_bp.route("/sync/<int:project_id>", methods=["POST"])
def sync_project(project_id):
    """Manually trigger GitHub sync for a project."""
    project = Project.query.get_or_404(project_id)
    if not project.github_repo:
        return jsonify({"error": "No GitHub repository connected"}), 400
    svc = _get_service()
    owner, repo = project.repository_owner, project.repository_name

    # Sync issues
    gh_issues = svc.get_issues(owner, repo, state="all", per_page=50)
    for gh_i in gh_issues:
        number = gh_i.get("number")
        existing = Issue.query.filter_by(project_id=project_id, github_issue_number=number).first()
        if not existing:
            labels_raw = gh_i.get("labels", [])
            labels_str = ",".join(l["name"] for l in labels_raw)
            is_bug = any("bug" in l["name"].lower() for l in labels_raw)
            new_issue = Issue(
                project_id=project_id,
                github_issue_number=number,
                title=gh_i.get("title", ""),
                state=gh_i.get("state", "open"),
                labels=labels_str,
                is_bug=is_bug,
                assignee=(gh_i.get("assignee") or {}).get("login"),
                author=(gh_i.get("user") or {}).get("login"),
                github_url=gh_i.get("html_url", ""),
            )
            db.session.add(new_issue)

    # Sync PRs
    gh_prs = svc.get_pull_requests(owner, repo, state="all")
    for gh_pr in gh_prs:
        number = gh_pr.get("number")
        existing = PullRequest.query.filter_by(project_id=project_id, github_pr_number=number).first()
        if not existing:
            new_pr = PullRequest(
                project_id=project_id,
                github_pr_number=number,
                title=gh_pr.get("title", ""),
                author=(gh_pr.get("user") or {}).get("login"),
                state=gh_pr.get("state", "open"),
                merged=gh_pr.get("merged", False),
                head_branch=(gh_pr.get("head") or {}).get("ref"),
                base_branch=(gh_pr.get("base") or {}).get("ref", "main"),
                github_url=gh_pr.get("html_url", ""),
            )
            db.session.add(new_pr)

    db.session.commit()
    return jsonify({"message": "Sync completed", "issues": len(gh_issues), "prs": len(gh_prs)})


def _demo_workflow_data():
    return {
        "total_count": 3,
        "workflows": [
            {"id": 1, "name": "TeamSync CI", "state": "active", "path": ".github/workflows/ci.yml"},
            {"id": 2, "name": "Code Quality", "state": "active", "path": ".github/workflows/quality.yml"},
            {"id": 3, "name": "Deploy", "state": "active", "path": ".github/workflows/deploy.yml"},
        ],
    }


def _demo_workflow_runs():
    return {
        "total_count": 12,
        "workflow_runs": [
            {"id": 1001, "name": "TeamSync CI", "status": "completed", "conclusion": "success",
             "head_branch": "feature/authentication", "event": "pull_request",
             "created_at": "2024-11-28T14:00:00Z", "run_number": 42,
             "html_url": "https://github.com/teamsync-demo/online-exam-system/actions/runs/1001"},
            {"id": 1002, "name": "Code Quality", "status": "completed", "conclusion": "failure",
             "head_branch": "feature/exam-module", "event": "pull_request",
             "created_at": "2024-11-28T10:30:00Z", "run_number": 41,
             "html_url": "https://github.com/teamsync-demo/online-exam-system/actions/runs/1002"},
            {"id": 1003, "name": "TeamSync CI", "status": "completed", "conclusion": "success",
             "head_branch": "main", "event": "push",
             "created_at": "2024-11-27T18:00:00Z", "run_number": 40,
             "html_url": "https://github.com/teamsync-demo/online-exam-system/actions/runs/1003"},
            {"id": 1004, "name": "Deploy", "status": "completed", "conclusion": "success",
             "head_branch": "main", "event": "push",
             "created_at": "2024-11-27T17:00:00Z", "run_number": 39,
             "html_url": "https://github.com/teamsync-demo/online-exam-system/actions/runs/1004"},
            {"id": 1005, "name": "Code Quality", "status": "in_progress", "conclusion": None,
             "head_branch": "bugfix/login-session", "event": "pull_request",
             "created_at": "2024-11-28T15:30:00Z", "run_number": 43,
             "html_url": "https://github.com/teamsync-demo/online-exam-system/actions/runs/1005"},
        ],
    }


# ─── Repository Access & Permission Control ──────────────────────────────────

@github_bp.route("/permissions", methods=["GET"])
def get_permissions():
    from ..models import RepoPermission, User
    project_id = request.args.get("project_id", 1, type=int)
    user_id = request.args.get("user_id", type=int)

    query = RepoPermission.query.filter_by(project_id=project_id)
    if user_id:
        perm = query.filter_by(user_id=user_id).first()
        if not perm:
            user = User.query.get(user_id)
            return jsonify({
                "user_id": user_id,
                "user_name": user.name if user else "Unknown",
                "github_username": user.github_username if user else "",
                "permission_level": "read",
                "status": "none",
                "can_modify": False,
            })
        data = perm.to_dict()
        data["can_modify"] = (perm.permission_level in ("write", "admin") and perm.status == "approved")
        return jsonify(data)

    perms = query.all()
    # Auto-initialize missing members if any
    all_users = User.query.filter_by(is_active=True).all()
    existing_uids = {p.user_id for p in perms}
    for u in all_users:
        if u.id not in existing_uids:
            is_lead = (u.role == "admin")
            p = RepoPermission(
                project_id=project_id,
                user_id=u.id,
                permission_level="admin" if is_lead else "read",
                status="approved" if is_lead else "none",
                request_reason="Repository Owner / Lead" if is_lead else None,
            )
            db.session.add(p)
            perms.append(p)
    db.session.commit()

    return jsonify([p.to_dict() for p in perms])


@github_bp.route("/permissions/request", methods=["POST"])
def request_permission():
    from ..models import RepoPermission, User, Notification
    from datetime import datetime
    data = request.get_json() or {}
    project_id = data.get("project_id", 1)
    user_id = data.get("user_id")
    reason = data.get("reason", "Requires write access for direct branch commits")
    perm_level = data.get("permission_level", "write")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    perm = RepoPermission.query.filter_by(project_id=project_id, user_id=user_id).first()
    if not perm:
        perm = RepoPermission(project_id=project_id, user_id=user_id)
        db.session.add(perm)

    perm.permission_level = perm_level
    perm.status = "requested"
    perm.request_reason = reason
    perm.requested_at = datetime.utcnow()
    perm.approved_at = None
    perm.approved_by_id = None

    # Alert repository owner
    project = Project.query.get(project_id)
    if project and project.owner_id:
        user = User.query.get(user_id)
        db.session.add(Notification(
            user_id=project.owner_id,
            title="🔒 Repo Access Request",
            message=f"{user.name if user else 'A developer'} requested '{perm_level}' permission on {project.name}: {reason}",
            type="warning",
            category="quality",
        ))

    db.session.commit()
    return jsonify({"message": "Permission request submitted to repository owner", "permission": perm.to_dict()})


@github_bp.route("/permissions/review", methods=["POST"])
def review_permission():
    from ..models import RepoPermission, Notification
    from datetime import datetime
    data = request.get_json() or {}
    permission_id = data.get("permission_id")
    user_id = data.get("user_id")
    project_id = data.get("project_id", 1)
    action = data.get("action", "approve")  # approve | reject | revoke
    reviewer_id = data.get("reviewer_id", 1)

    perm = None
    if permission_id:
        perm = RepoPermission.query.get(permission_id)
    elif user_id:
        perm = RepoPermission.query.filter_by(project_id=project_id, user_id=user_id).first()

    if not perm:
        return jsonify({"error": "Permission record not found"}), 404

    if action == "approve":
        perm.status = "approved"
        perm.permission_level = "write"
        perm.approved_at = datetime.utcnow()
        perm.approved_by_id = reviewer_id
        msg = "Write access to repository was approved by the owner."
        notif_type = "success"
    elif action == "reject":
        perm.status = "rejected"
        perm.approved_at = None
        perm.approved_by_id = reviewer_id
        msg = "Write access request was rejected by the owner."
        notif_type = "error"
    else:  # revoke
        perm.status = "none"
        perm.permission_level = "read"
        perm.request_reason = None
        msg = "Repository write access was revoked."
        notif_type = "warning"

    # Notify member
    db.session.add(Notification(
        user_id=perm.user_id,
        title="🔒 Repository Permission Updated",
        message=msg,
        type=notif_type,
        category="quality",
    ))

    db.session.commit()
    return jsonify({"message": f"Permission {action}d successfully", "permission": perm.to_dict()})


@github_bp.route("/commit", methods=["POST"])
def make_commit():
    from ..models import RepoPermission, RepoCommit, QualityReport
    from datetime import datetime
    import hashlib
    import random

    data = request.get_json() or {}
    project_id = data.get("project_id", 1)
    user_id = data.get("user_id")
    branch = data.get("branch", "develop")
    file_path = data.get("file_path", "backend/main.py")
    file_content = data.get("file_content", "")
    message = data.get("message", "chore: direct update to repository")

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    # Authorization Check
    project = Project.query.get(project_id)
    is_owner = (project and project.owner_id == user_id)
    perm = RepoPermission.query.filter_by(project_id=project_id, user_id=user_id).first()
    has_write = perm and (perm.permission_level in ("write", "admin") and perm.status == "approved")

    if not (is_owner or has_write):
        return jsonify({
            "error": "Forbidden: You do not have write permission on this repository. Request authorization from the owner first.",
            "authorized": False,
        }), 403

    # Generate realistic commit SHA
    raw = f"{user_id}-{branch}-{message}-{datetime.utcnow().isoformat()}"
    sha = hashlib.sha1(raw.encode()).hexdigest()[:7]

    commit = RepoCommit(
        project_id=project_id,
        user_id=user_id,
        sha=sha,
        branch=branch,
        message=message,
        file_path=file_path,
    )
    db.session.add(commit)

    # Trigger automatic code-quality / CI check simulation
    ci_status = "passed" if "test" in message or "fix" in message or random.random() > 0.3 else "failed"
    db.session.add(QualityReport(
        project_id=project_id,
        tool_name="ruff",
        status=ci_status,
        summary=f"Automated CI lint scan for commit [{sha}] on branch '{branch}': All checks validated.",
        issues_found=0 if ci_status == "passed" else 2,
    ))

    db.session.commit()
    return jsonify({
        "message": f"Changes committed and pushed successfully to '{branch}'",
        "commit": commit.to_dict(),
        "ci_status": ci_status,
    })


@github_bp.route("/commits-live", methods=["GET"])
def get_live_commits():
    from ..models import RepoCommit
    project_id = request.args.get("project_id", 1, type=int)
    db_commits = RepoCommit.query.filter_by(project_id=project_id)\
        .order_by(RepoCommit.created_at.desc()).all()

    # Prepend dynamic commits to demo commits
    demo = GitHubService.get_demo_data()["recent_commits"]
    live = []
    for c in db_commits:
        author_name = c.user.name if c.user else "Unknown"
        live.append({
            "sha": c.sha,
            "commit": {
                "message": f"[{c.branch}] {c.message}",
                "author": {"name": author_name, "date": c.created_at.isoformat()},
            },
            "file_path": c.file_path,
            "is_dynamic": True,
        })
    live.extend(demo)
    return jsonify(live)
