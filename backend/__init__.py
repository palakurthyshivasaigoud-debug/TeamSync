# pyrefly: ignore-errors[unexpected-keyword]
# SQLAlchemy db.Model subclasses generate __init__ dynamically via metaclass;
# Pyrefly cannot statically infer those keyword arguments — suppressed project-wide.
from datetime import date, datetime, timezone, timedelta
from flask import Flask
from flask_cors import CORS
from .extensions import db, bcrypt, login_manager
from .config import get_config
from .models import (
    User,
    Project,
    ProjectMember,
    Task,
    Issue,
    PullRequest,
    Milestone,
    QualityReport,
    RepoPermission,
    RepoCommit,
)
from .routes.auth import auth_bp
from .routes.projects import projects_bp
from .routes.tasks import tasks_bp
from .routes.github import github_bp
from .routes.analytics import analytics_bp
from .routes.webhooks import webhooks_bp
from .routes.team import team_bp
from .routes.quality import quality_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(github_bp, url_prefix="/api/github")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(webhooks_bp, url_prefix="/api/webhooks")
    app.register_blueprint(team_bp, url_prefix="/api/team")
    app.register_blueprint(quality_bp, url_prefix="/api/quality")

    with app.app_context():
        db.create_all()
        _seed_demo_data()

    @app.route("/api/health")
    def health():
        return {"status": "ok", "app": "TeamSync API", "version": "1.0.0"}

    return app


def _seed_demo_data():
    """Seed realistic demo data on first run."""
    if User.query.count() > 0:
        return  # Already seeded

    # Create users
    users_data = [
        ("Priya Sharma", "priya@teamsync.dev", "password123", "admin", "priya-sharma"),
        ("Arjun Mehta", "arjun@teamsync.dev", "password123", "developer", "arjun-mehta"),
        ("Divya Reddy", "divya@teamsync.dev", "password123", "developer", "divya-reddy"),
        ("Rohan Gupta", "rohan@teamsync.dev", "password123", "qa", "rohan-gupta"),
        ("Sneha Patel", "sneha@teamsync.dev", "password123", "developer", "sneha-patel"),
    ]
    users = []
    for name, email, pwd, role, gh in users_data:
        u = User(name=name, email=email, role=role, github_username=gh)
        u.set_password(pwd)
        db.session.add(u)
        users.append(u)
    db.session.flush()

    today = date.today()
    now = datetime.now(timezone.utc)

    # Create project
    p = Project(
        name="Online Examination System",
        description="AI-based examination platform with real-time proctoring, automatic evaluation, and detailed analytics.",
        owner_id=users[0].id,
        repository_owner="teamsync-demo",
        repository_name="online-exam-system",
        start_date=today - timedelta(days=30),
        deadline=today + timedelta(days=16),
        status="active",
        tech_stack="Python, Flask, SQLite, React, GitHub Actions",
    )
    db.session.add(p)
    db.session.flush()

    # Add members
    roles = ["lead", "developer", "developer", "qa", "developer"]
    for i, u in enumerate(users):
        db.session.add(ProjectMember(project_id=p.id, user_id=u.id, project_role=roles[i]))

    # Tasks
    task_defs = [
        ("User Authentication Module", users[1].id, "completed", "high", today - timedelta(days=5)),
        ("Database Schema Design", users[1].id, "completed", "high", today - timedelta(days=10)),
        ("Exam Question Bank API", users[2].id, "in_progress", "high", today + timedelta(days=3)),
        ("Student Dashboard UI", users[2].id, "in_progress", "medium", today + timedelta(days=5)),
        ("Result Generation Engine", users[4].id, "todo", "critical", today + timedelta(days=8)),
        ("Proctoring Integration", users[4].id, "todo", "medium", today + timedelta(days=12)),
        ("Unit Test Suite", users[3].id, "in_review", "high", today + timedelta(days=2)),
        ("CI/CD Pipeline Setup", users[1].id, "completed", "medium", today - timedelta(days=3)),
        ("API Documentation", users[4].id, "todo", "low", today + timedelta(days=14)),
        ("Performance Optimization", users[2].id, "blocked", "medium", today + timedelta(days=10)),
        ("Email Notification System", users[4].id, "todo", "low", today + timedelta(days=15)),
        ("Admin Panel", users[1].id, "in_progress", "high", today + timedelta(days=6)),
    ]
    for i, (title, uid, status, priority, due) in enumerate(task_defs, 1):
        t = Task(
            project_id=p.id,
            assigned_user_id=uid,
            title=title,
            description=f"Implementation of {title} as part of the Online Examination System.",
            priority=priority,
            status=status,
            due_date=due,
            github_issue_number=i,
        )
        if status == "completed":
            t.completed_at = now - timedelta(days=2)
        db.session.add(t)

    # Issues
    issue_defs = [
        (1, "Login button unresponsive after failed attempt", "open", "bug,authentication", True, users[1].github_username),
        (2, "Implement exam timer with auto-submit", "open", "enhancement,exam", False, users[2].github_username),
        (3, "Database connection pool exhaustion under load", "open", "bug,performance", True, users[1].github_username),
        (4, "Add pagination to question list API", "closed", "enhancement", False, users[4].github_username),
        (5, "Student result PDF export", "open", "feature,results", False, users[4].github_username),
        (6, "Session token not invalidated on logout", "open", "bug,security", True, users[1].github_username),
        (7, "Mobile responsive fixes for exam screen", "closed", "bug,ui", True, users[2].github_username),
        (8, "Add GitHub Actions badge to README", "closed", "documentation", False, users[1].github_username),
    ]
    for num, title, state, labels, is_bug, assignee in issue_defs:
        db.session.add(Issue(
            project_id=p.id,
            github_issue_number=num,
            title=title,
            state=state,
            labels=labels,
            assignee=assignee,
            author=users[0].github_username,
            is_bug=is_bug,
            github_url=f"https://github.com/teamsync-demo/online-exam-system/issues/{num}",
        ))

    # Pull Requests
    pr_defs = [
        (12, "feat: Complete JWT authentication system", users[1].github_username, "closed", True, "feature/authentication", "main", "approved", "passed"),
        (13, "feat: Exam module core logic", users[2].github_username, "open", False, "feature/exam-module", "main", "pending", "failed"),
        (14, "ci: Add Ruff and Bandit to GitHub Actions", users[1].github_username, "closed", True, "ci/setup-actions", "main", "approved", "passed"),
        (15, "test: Pytest suite for auth module", users[3].github_username, "open", False, "feature/tests", "main", "changes_requested", "passed"),
        (16, "feat: Admin panel CRUD operations", users[1].github_username, "open", False, "feature/admin", "develop", "pending", "pending"),
        (17, "fix: Session timeout and logout bug", users[2].github_username, "open", False, "bugfix/login-session", "main", "pending", "failed"),
    ]
    for num, title, author, state, merged, head, base, review, checks in pr_defs:
        pr = PullRequest(
            project_id=p.id,
            github_pr_number=num,
            title=title,
            author=author,
            state=state,
            merged=merged,
            head_branch=head,
            base_branch=base,
            review_status=review,
            check_status=checks,
            changed_files=12,
            additions=245,
            deletions=31,
            github_url=f"https://github.com/teamsync-demo/online-exam-system/pull/{num}",
        )
        if merged:
            pr.merged_at = now - timedelta(days=3)
        db.session.add(pr)

    # Milestones
    milestone_defs = [
        ("Core Authentication", today - timedelta(days=2), "closed", 0, 4),
        ("Backend API v1", today + timedelta(days=5), "open", 5, 3),
        ("Frontend MVP", today + timedelta(days=12), "open", 8, 1),
        ("Testing & QA", today + timedelta(days=15), "open", 6, 0),
        ("Production Release v1.0", today + timedelta(days=16), "open", 12, 2),
    ]
    for title, due, status, open_i, closed_i in milestone_defs:
        db.session.add(Milestone(
            project_id=p.id,
            title=title,
            due_date=due,
            status=status,
            open_issues=open_i,
            closed_issues=closed_i,
        ))

    # Quality Reports
    qr_defs = [
        (16, "ruff", "passed", "No linting issues found. All code follows PEP 8.", 0),
        (16, "bandit", "passed", "No security vulnerabilities detected.", 0),
        (16, "pytest", "failed", "3 tests failed: test_exam_submit, test_result_calc, test_timer_auto_submit", 3),
        (15, "ruff", "passed", "0 errors, 2 warnings (line length).", 2),
        (15, "pytest", "passed", "42/42 tests passed. Coverage: 87%.", 0),
        (14, "ruff", "passed", "Code quality checks passed.", 0),
        (14, "bandit", "passed", "Security scan clean.", 0),
        (13, "ruff", "failed", "12 linting issues found: unused imports, undefined variables.", 12),
        (13, "pytest", "failed", "8 tests failed. Coverage dropped to 62%.", 8),
    ]
    for pr_num, tool, status, summary, count in qr_defs:
        db.session.add(QualityReport(
            project_id=p.id,
            github_pr_number=pr_num,
            tool_name=tool,
            status=status,
            summary=summary,
            issues_found=count,
        ))

    # Seed Repo Permissions (Access Control Demonstration)
    permissions_data = [
        (users[0].id, "admin", "approved", "Repository Owner / Tech Lead", users[0].id),
        (users[1].id, "write", "approved", "Backend lead needs direct commit access to feature branches", users[0].id),
        (users[4].id, "write", "requested", "Requesting write authorization to commit result calculation algorithm directly to feature/result-generation", None),
        (users[2].id, "read", "none", None, None),
        (users[3].id, "read", "none", None, None),
    ]
    for uid, plevel, pstatus, reason, app_by in permissions_data:
        db.session.add(RepoPermission(
            project_id=p.id,
            user_id=uid,
            permission_level=plevel,
            status=pstatus,
            request_reason=reason,
            requested_at=now - timedelta(hours=2) if reason else None,
            approved_at=now - timedelta(days=5) if pstatus == "approved" else None,
            approved_by_id=app_by,
        ))

    # Initial Commit
    db.session.add(RepoCommit(
        project_id=p.id,
        user_id=users[1].id,
        sha="c4f82a1",
        branch="feature/authentication",
        message="feat(auth): add JWT bearer validation middleware",
        file_path="backend/services/auth_service.py",
        created_at=now - timedelta(hours=3),
    ))

    db.session.commit()
