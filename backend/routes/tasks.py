from flask import Blueprint, request, jsonify
from datetime import date, datetime
from ..models import Task
from ..extensions import db

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["GET"])
def list_tasks():
    project_id = request.args.get("project_id", type=int)
    status = request.args.get("status")
    assigned = request.args.get("assigned_user_id", type=int)
    query = Task.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if status:
        query = query.filter_by(status=status)
    if assigned:
        query = query.filter_by(assigned_user_id=assigned)
    tasks = query.order_by(Task.due_date.asc()).all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data or "project_id" not in data:
        return jsonify({"error": "title and project_id required"}), 400
    task = Task(
        project_id=data["project_id"],
        title=data["title"],
        description=data.get("description", ""),
        assigned_user_id=data.get("assigned_user_id"),
        priority=data.get("priority", "medium"),
        status=data.get("status", "todo"),
        due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
        github_issue_number=data.get("github_issue_number"),
        estimated_hours=data.get("estimated_hours"),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json() or {}
    for field in ("title", "description", "priority", "status", "assigned_user_id",
                  "github_issue_number", "github_pr_number", "estimated_hours", "actual_hours"):
        if field in data:
            setattr(task, field, data[field])
    if "due_date" in data and data["due_date"]:
        task.due_date = date.fromisoformat(data["due_date"])
    if data.get("status") == "completed" and not task.completed_at:
        task.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})
