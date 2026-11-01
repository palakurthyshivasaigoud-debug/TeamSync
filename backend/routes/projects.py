from flask import Blueprint, request, jsonify
from datetime import date
from ..models import Project, ProjectMember
from ..extensions import db

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/", methods=["GET"])
def list_projects():
    projects = Project.query.filter(Project.status != "archived").all()
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route("/", methods=["POST"])
def create_project():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Project name is required"}), 400
    project = Project(
        name=data["name"],
        description=data.get("description", ""),
        owner_id=data.get("owner_id", 1),
        repository_owner=data.get("repository_owner"),
        repository_name=data.get("repository_name"),
        start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else date.today(),
        deadline=date.fromisoformat(data["deadline"]) if data.get("deadline") else None,
        status=data.get("status", "active"),
        tech_stack=data.get("tech_stack", ""),
    )
    db.session.add(project)
    db.session.flush()
    # Auto-add owner as lead
    db.session.add(ProjectMember(
        project_id=project.id, user_id=project.owner_id, project_role="lead"
    ))
    db.session.commit()
    return jsonify(project.to_dict()), 201


@projects_bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id):
    p = Project.query.get_or_404(project_id)
    data = p.to_dict()
    data["members"] = [
        {"user": m.user.to_dict(), "role": m.project_role}
        for m in p.members
    ]
    return jsonify(data)


@projects_bp.route("/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    p = Project.query.get_or_404(project_id)
    data = request.get_json() or {}
    for field in ("name", "description", "status", "tech_stack"):
        if field in data:
            setattr(p, field, data[field])
    if "deadline" in data and data["deadline"]:
        p.deadline = date.fromisoformat(data["deadline"])
    if "repository_owner" in data:
        p.repository_owner = data["repository_owner"]
    if "repository_name" in data:
        p.repository_name = data["repository_name"]
    db.session.commit()
    return jsonify(p.to_dict())


@projects_bp.route("/<int:project_id>", methods=["DELETE"])
def archive_project(project_id):
    p = Project.query.get_or_404(project_id)
    p.status = "archived"
    db.session.commit()
    return jsonify({"message": "Project archived"})


@projects_bp.route("/<int:project_id>/members", methods=["POST"])
def add_member(project_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        return jsonify({"error": "User already a member"}), 409
    m = ProjectMember(project_id=project_id, user_id=user_id, project_role=data.get("role", "developer"))
    db.session.add(m)
    db.session.commit()
    return jsonify({"message": "Member added"}), 201
