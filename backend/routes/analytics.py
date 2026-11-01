from flask import Blueprint, request, jsonify
from ..services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/overview", methods=["GET"])
def overview():
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        summaries = AnalyticsService.get_all_projects_summary()
        return jsonify({"projects": summaries})
    data = AnalyticsService.get_project_overview(project_id)
    return jsonify(data)


@analytics_bp.route("/workload", methods=["GET"])
def workload():
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    return jsonify(AnalyticsService.get_developer_workload(project_id))


@analytics_bp.route("/weekly", methods=["GET"])
def weekly():
    project_id = request.args.get("project_id", type=int)
    weeks = request.args.get("weeks", 8, type=int)
    if not project_id:
        return jsonify({"error": "project_id required"}), 400
    return jsonify(AnalyticsService.get_weekly_activity(project_id, weeks))


@analytics_bp.route("/all-projects", methods=["GET"])
def all_projects():
    return jsonify(AnalyticsService.get_all_projects_summary())
