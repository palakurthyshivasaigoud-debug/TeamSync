from datetime import datetime, timezone
from flask_login import UserMixin
from .extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="developer")          # admin | developer | qa | viewer
    github_username = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    owned_projects = db.relationship("Project", backref="owner", lazy=True, foreign_keys="Project.owner_id")
    tasks = db.relationship("Task", backref="assignee", lazy=True, foreign_keys="Task.assigned_user_id")
    notifications = db.relationship("Notification", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "github_username": self.github_username,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat(),
        }


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    repository_owner = db.Column(db.String(100), nullable=True)
    repository_name = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="active")           # active | completed | on-hold | archived
    tech_stack = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    members = db.relationship("ProjectMember", backref="project", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")
    issues = db.relationship("Issue", backref="project", lazy=True, cascade="all, delete-orphan")
    pull_requests = db.relationship("PullRequest", backref="project", lazy=True, cascade="all, delete-orphan")
    milestones = db.relationship("Milestone", backref="project", lazy=True, cascade="all, delete-orphan")
    quality_reports = db.relationship("QualityReport", backref="project", lazy=True, cascade="all, delete-orphan")

    @property
    def github_repo(self):
        if self.repository_owner and self.repository_name:
            return f"{self.repository_owner}/{self.repository_name}"
        return None

    def to_dict(self):
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == "completed"])
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "repository_owner": self.repository_owner,
            "repository_name": self.repository_name,
            "github_repo": self.github_repo,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "tech_stack": self.tech_stack,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 1),
            "created_at": self.created_at.isoformat(),
        }


class ProjectMember(db.Model):
    __tablename__ = "project_members"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    project_role = db.Column(db.String(100), default="developer")  # lead | developer | qa | viewer
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="project_memberships")


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default="medium")         # low | medium | high | critical
    status = db.Column(db.String(50), default="todo")             # todo | in_progress | in_review | completed | blocked
    due_date = db.Column(db.Date, nullable=True)
    github_issue_number = db.Column(db.Integer, nullable=True)
    github_pr_number = db.Column(db.Integer, nullable=True)
    estimated_hours = db.Column(db.Float, nullable=True)
    actual_hours = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    def is_overdue(self):
        if self.due_date and self.status not in ("completed",):
            return datetime.now(timezone.utc).date() > self.due_date
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "assigned_user_id": self.assigned_user_id,
            "assignee_name": self.assignee.name if self.assignee else None,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "github_issue_number": self.github_issue_number,
            "github_pr_number": self.github_pr_number,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "is_overdue": self.is_overdue(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Issue(db.Model):
    __tablename__ = "issues"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    github_issue_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(20), default="open")              # open | closed
    labels = db.Column(db.String(500), nullable=True)
    assignee = db.Column(db.String(100), nullable=True)
    author = db.Column(db.String(100), nullable=True)
    milestone = db.Column(db.String(200), nullable=True)
    github_url = db.Column(db.String(500), nullable=True)
    is_bug = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "github_issue_number": self.github_issue_number,
            "title": self.title,
            "body": self.body,
            "state": self.state,
            "labels": self.labels.split(",") if self.labels else [],
            "assignee": self.assignee,
            "author": self.author,
            "milestone": self.milestone,
            "github_url": self.github_url,
            "is_bug": self.is_bug,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class PullRequest(db.Model):
    __tablename__ = "pull_requests"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    github_pr_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(20), default="open")              # open | closed
    merged = db.Column(db.Boolean, default=False)
    draft = db.Column(db.Boolean, default=False)
    head_branch = db.Column(db.String(200), nullable=True)
    base_branch = db.Column(db.String(200), default="main")
    review_status = db.Column(db.String(50), default="pending")   # pending | approved | changes_requested
    check_status = db.Column(db.String(50), default="pending")    # pending | passed | failed
    changed_files = db.Column(db.Integer, default=0)
    additions = db.Column(db.Integer, default=0)
    deletions = db.Column(db.Integer, default=0)
    github_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    merged_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "github_pr_number": self.github_pr_number,
            "title": self.title,
            "author": self.author,
            "state": self.state,
            "merged": self.merged,
            "draft": self.draft,
            "head_branch": self.head_branch,
            "base_branch": self.base_branch,
            "review_status": self.review_status,
            "check_status": self.check_status,
            "changed_files": self.changed_files,
            "additions": self.additions,
            "deletions": self.deletions,
            "github_url": self.github_url,
            "created_at": self.created_at.isoformat(),
            "merged_at": self.merged_at.isoformat() if self.merged_at else None,
        }


class Milestone(db.Model):
    __tablename__ = "milestones"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    github_milestone_number = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="open")             # open | closed
    open_issues = db.Column(db.Integer, default=0)
    closed_issues = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def progress(self):
        total = self.open_issues + self.closed_issues
        return round((self.closed_issues / total * 100) if total > 0 else 0, 1)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "open_issues": self.open_issues,
            "closed_issues": self.closed_issues,
            "progress": self.progress,
        }


class QualityReport(db.Model):
    __tablename__ = "quality_reports"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    github_pr_number = db.Column(db.Integer, nullable=True)
    github_commit_sha = db.Column(db.String(50), nullable=True)
    tool_name = db.Column(db.String(50), nullable=False)          # ruff | bandit | pytest | github_actions
    status = db.Column(db.String(20), default="pending")          # pending | passed | failed | skipped
    summary = db.Column(db.Text, nullable=True)
    issues_found = db.Column(db.Integer, default=0)
    ai_explanation = db.Column(db.Text, nullable=True)
    workflow_run_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "github_pr_number": self.github_pr_number,
            "tool_name": self.tool_name,
            "status": self.status,
            "summary": self.summary,
            "issues_found": self.issues_found,
            "ai_explanation": self.ai_explanation,
            "created_at": self.created_at.isoformat(),
        }


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default="info")               # info | warning | error | success
    category = db.Column(db.String(50), nullable=True)            # task | pr | issue | deadline | quality
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "category": self.category,
            "is_read": self.is_read,
            "link": self.link,
            "created_at": self.created_at.isoformat(),
        }


class RepoPermission(db.Model):
    __tablename__ = "repo_permissions"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    permission_level = db.Column(db.String(50), default="read")  # read | write | admin
    status = db.Column(db.String(50), default="none")  # none | requested | approved | rejected
    request_reason = db.Column(db.String(500), nullable=True)
    requested_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    user = db.relationship("User", foreign_keys=[user_id])
    approver = db.relationship("User", foreign_keys=[approved_by_id])

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown",
            "github_username": self.user.github_username if self.user else "",
            "role": self.user.role if self.user else "developer",
            "permission_level": self.permission_level,
            "status": self.status,
            "request_reason": self.request_reason,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approver.name if self.approver else None,
        }


class RepoCommit(db.Model):
    __tablename__ = "repo_commits"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sha = db.Column(db.String(40), nullable=False)
    branch = db.Column(db.String(100), default="main")
    message = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "sha": self.sha,
            "branch": self.branch,
            "message": self.message,
            "file_path": self.file_path,
            "author_name": self.user.name if self.user else "Unknown",
            "author_github": self.user.github_username if self.user else "",
            "created_at": self.created_at.isoformat(),
        }


class WebhookEvent(db.Model):
    __tablename__ = "webhook_events"
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.String(100), unique=True, nullable=True)
    event_type = db.Column(db.String(100), nullable=False)
    repository = db.Column(db.String(200), nullable=True)
    payload = db.Column(db.Text, nullable=True)
    processed = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
