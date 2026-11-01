from flask import Blueprint, request, jsonify
from ..models import QualityReport
from ..extensions import db

quality_bp = Blueprint("quality", __name__)


@quality_bp.route("/<int:project_id>", methods=["GET"])
def get_quality_reports(project_id):
    reports = QualityReport.query.filter_by(project_id=project_id)\
        .order_by(QualityReport.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reports])


@quality_bp.route("/", methods=["POST"])
def create_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Data required"}), 400
    report = QualityReport(
        project_id=data["project_id"],
        github_pr_number=data.get("github_pr_number"),
        github_commit_sha=data.get("github_commit_sha"),
        tool_name=data.get("tool_name", "ruff"),
        status=data.get("status", "pending"),
        summary=data.get("summary", ""),
        issues_found=data.get("issues_found", 0),
        ai_explanation=data.get("ai_explanation"),
        workflow_run_url=data.get("workflow_run_url"),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify(report.to_dict()), 201


@quality_bp.route("/summary/<int:project_id>", methods=["GET"])
def quality_summary(project_id):
    reports = QualityReport.query.filter_by(project_id=project_id).all()
    tools = {}
    for r in reports:
        if r.tool_name not in tools:
            tools[r.tool_name] = {"passed": 0, "failed": 0, "total": 0}
        tools[r.tool_name]["total"] += 1
        tools[r.tool_name][r.status if r.status in ("passed", "failed") else "failed"] += 1

    return jsonify({
        "project_id": project_id,
        "total_reports": len(reports),
        "by_tool": tools,
        "overall_pass_rate": round(
            (len([r for r in reports if r.status == "passed"]) / len(reports) * 100) if reports else 0, 1
        ),
    })
