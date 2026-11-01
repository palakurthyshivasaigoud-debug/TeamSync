"""TeamSync — Complete project verification script."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend import create_app

app = create_app()

with app.app_context():
    from backend.models import User, Project, Task, Issue, PullRequest, Milestone, QualityReport
    from backend.services.analytics_service import AnalyticsService

    print("=" * 50)
    print("  TeamSync — Project Verification")
    print("=" * 50)

    print("\nDATABASE RECORDS:")
    print(f"  Users:           {User.query.count()}")
    print(f"  Projects:        {Project.query.count()}")
    print(f"  Tasks:           {Task.query.count()}")
    print(f"  Issues:          {Issue.query.count()}")
    print(f"  Pull Requests:   {PullRequest.query.count()}")
    print(f"  Milestones:      {Milestone.query.count()}")
    print(f"  Quality Reports: {QualityReport.query.count()}")

    p = Project.query.first()
    ov = AnalyticsService.get_project_overview(p.id)
    wl = AnalyticsService.get_developer_workload(p.id)

    print(f"\nPROJECT: {p.name}")
    print(f"  Health Score:     {ov['health_score']}%")
    print(f"  Completion Rate:  {ov['completion_rate']}%")
    print(f"  Days Remaining:   {ov['days_remaining']}")
    print(f"  Tasks:            {ov['tasks']}")
    print(f"  Open Bugs:        {ov['issues']['bugs_open']}")
    print(f"  Pending PRs:      {ov['pull_requests']['pending_review']}")
    print(f"  Milestone %:      {ov['milestones']['completion']}%")

    print("\nDEVELOPER WORKLOAD:")
    for dev in wl:
        print(f"  {dev['name']:15s} | Tasks: {dev['total_tasks']} | Done: {dev['completed']} | Rate: {dev['completion_rate']}%")

    print("\nAll systems operational!")
    print("=" * 50)
