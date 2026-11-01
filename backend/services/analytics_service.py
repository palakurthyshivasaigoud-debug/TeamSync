from datetime import datetime, date, timedelta
from ..models import Task, Project, ProjectMember


class AnalyticsService:
    """Compute and return project analytics and developer productivity metrics."""

    @staticmethod
    def get_project_overview(project_id: int) -> dict:
        project = Project.query.get(project_id)
        if not project:
            return {}

        tasks = project.tasks
        issues = project.issues
        prs = project.pull_requests
        milestones = project.milestones

        total_tasks = len(tasks)
        completed = [t for t in tasks if t.status == "completed"]
        in_progress = [t for t in tasks if t.status == "in_progress"]
        in_review = [t for t in tasks if t.status == "in_review"]
        todo = [t for t in tasks if t.status == "todo"]
        blocked = [t for t in tasks if t.status == "blocked"]
        overdue = [t for t in tasks if t.is_overdue()]

        open_issues = [i for i in issues if i.state == "open"]
        bugs = [i for i in issues if i.is_bug]
        open_bugs = [b for b in bugs if b.state == "open"]

        open_prs = [pr for pr in prs if pr.state == "open" and not pr.merged]
        merged_prs = [pr for pr in prs if pr.merged]
        pending_review = [pr for pr in open_prs if pr.review_status == "pending"]
        failed_checks = [pr for pr in open_prs if pr.check_status == "failed"]

        completion_rate = round((len(completed) / total_tasks * 100) if total_tasks > 0 else 0, 1)
        bug_resolution_rate = round(((len(bugs) - len(open_bugs)) / len(bugs) * 100) if bugs else 100, 1)
        pr_merge_rate = round((len(merged_prs) / (len(merged_prs) + len(open_prs)) * 100) if (merged_prs or open_prs) else 0, 1)

        # Project health score: H = 0.4*T + 0.3*M + 0.2*B + 0.1*C
        milestone_completion = AnalyticsService._get_milestone_completion(milestones)
        quality_reports = project.quality_reports
        ci_success = AnalyticsService._get_ci_score(quality_reports)

        health_score = round(
            0.4 * completion_rate +
            0.3 * milestone_completion +
            0.2 * bug_resolution_rate +
            0.1 * ci_success, 1
        )

        # Days until deadline
        days_remaining = None
        if project.deadline:
            delta = project.deadline - date.today()
            days_remaining = delta.days

        return {
            "project_id": project_id,
            "project_name": project.name,
            "health_score": health_score,
            "completion_rate": completion_rate,
            "days_remaining": days_remaining,
            "tasks": {
                "total": total_tasks,
                "completed": len(completed),
                "in_progress": len(in_progress),
                "in_review": len(in_review),
                "todo": len(todo),
                "blocked": len(blocked),
                "overdue": len(overdue),
            },
            "issues": {
                "total": len(issues),
                "open": len(open_issues),
                "closed": len(issues) - len(open_issues),
                "bugs_total": len(bugs),
                "bugs_open": len(open_bugs),
            },
            "pull_requests": {
                "total": len(prs),
                "open": len(open_prs),
                "merged": len(merged_prs),
                "pending_review": len(pending_review),
                "failed_checks": len(failed_checks),
                "merge_rate": pr_merge_rate,
            },
            "milestones": {
                "total": len(milestones),
                "completion": milestone_completion,
            },
            "bug_resolution_rate": bug_resolution_rate,
            "ci_success_rate": ci_success,
        }

    @staticmethod
    def get_developer_workload(project_id: int) -> list:
        """Return per-developer task workload for a project."""
        members = ProjectMember.query.filter_by(project_id=project_id).all()
        workloads = []
        for member in members:
            user = member.user
            tasks = Task.query.filter_by(project_id=project_id, assigned_user_id=user.id).all()
            completed = [t for t in tasks if t.status == "completed"]
            in_progress = [t for t in tasks if t.status == "in_progress"]
            overdue = [t for t in tasks if t.is_overdue()]
            workloads.append({
                "user_id": user.id,
                "name": user.name,
                "role": member.project_role,
                "github_username": user.github_username,
                "total_tasks": len(tasks),
                "completed": len(completed),
                "in_progress": len(in_progress),
                "overdue": len(overdue),
                "completion_rate": round((len(completed) / len(tasks) * 100) if tasks else 0, 1),
            })
        return sorted(workloads, key=lambda x: x["total_tasks"], reverse=True)

    @staticmethod
    def get_weekly_activity(project_id: int, weeks: int = 8) -> list:
        """Return weekly task completion counts for the last N weeks."""
        results = []
        today = date.today()
        for i in range(weeks - 1, -1, -1):
            week_start = today - timedelta(days=today.weekday() + 7 * i)
            week_end = week_start + timedelta(days=6)
            completed = Task.query.filter(
                Task.project_id == project_id,
                Task.status == "completed",
                Task.completed_at >= datetime.combine(week_start, datetime.min.time()),
                Task.completed_at <= datetime.combine(week_end, datetime.max.time()),
            ).count()
            results.append({
                "week": week_start.strftime("W%V"),
                "label": week_start.strftime("%b %d"),
                "completed": completed,
            })
        return results

    @staticmethod
    def get_all_projects_summary() -> list:
        """Return summary analytics for all projects."""
        projects = Project.query.filter(Project.status != "archived").all()
        summaries = []
        for p in projects:
            tasks = p.tasks
            total = len(tasks)
            completed = len([t for t in tasks if t.status == "completed"])
            overdue = len([t for t in tasks if t.is_overdue()])
            open_prs = len([pr for pr in p.pull_requests if pr.state == "open" and not pr.merged])
            open_bugs = len([i for i in p.issues if i.is_bug and i.state == "open"])
            summaries.append({
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "completion_rate": round((completed / total * 100) if total > 0 else 0, 1),
                "total_tasks": total,
                "completed_tasks": completed,
                "overdue_tasks": overdue,
                "open_prs": open_prs,
                "open_bugs": open_bugs,
                "deadline": p.deadline.isoformat() if p.deadline else None,
                "days_remaining": (p.deadline - date.today()).days if p.deadline else None,
            })
        return summaries

    @staticmethod
    def _get_milestone_completion(milestones) -> float:
        if not milestones:
            return 100.0
        total_closed = sum(m.closed_issues for m in milestones)
        total_all = sum(m.open_issues + m.closed_issues for m in milestones)
        return round((total_closed / total_all * 100) if total_all > 0 else 0, 1)

    @staticmethod
    def _get_ci_score(quality_reports) -> float:
        if not quality_reports:
            return 100.0
        passed = len([r for r in quality_reports if r.status == "passed"])
        return round((passed / len(quality_reports) * 100) if quality_reports else 100, 1)
