from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from ..models import ProjectMember, User, RepoPermission
from ..extensions import db

team_bp = Blueprint("team", __name__)


@team_bp.route("/members", methods=["GET"])
def get_members():
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        users = User.query.filter_by(is_active=True).all()
        return jsonify([u.to_dict() for u in users])
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify([
        {"user": m.user.to_dict(), "role": m.project_role, "joined_at": m.joined_at.isoformat()}
        for m in members
    ])


@team_bp.route("/invite", methods=["POST"])
def invite_member():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    github_username = data.get("github_username", "").strip()
    role = data.get("role", "developer")
    project_id = data.get("project_id", 1)

    if not name or not github_username:
        return jsonify({"error": "Name and GitHub username are required"}), 400

    if not email:
        email = f"{github_username.lower().replace('-', '_')}@teamsync.dev"

    user = User.query.filter((User.email == email) | (User.github_username == github_username)).first()
    if not user:
        user = User(
            name=name,
            email=email,
            role=role,
            github_username=github_username,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.flush()

    m = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
    if not m:
        m = ProjectMember(project_id=project_id, user_id=user.id, project_role=role)
        db.session.add(m)

    perm = RepoPermission.query.filter_by(project_id=project_id, user_id=user.id).first()
    if not perm:
        auto_app = data.get("auto_approve", True)
        perm = RepoPermission(
            project_id=project_id,
            user_id=user.id,
            permission_level=data.get("permission_level", "write"),
            status="approved" if auto_app else "requested",
            request_reason="Collaborator invite by Project Lead",
            requested_at=datetime.now(timezone.utc),
            approved_at=datetime.now(timezone.utc) if auto_app else None,
            approved_by_id=1 if auto_app else None,
        )
        db.session.add(perm)

    db.session.commit()
    return jsonify({"message": f"Successfully added {name} as project collaborator", "user": user.to_dict()}), 201


@team_bp.route("/remove-member", methods=["DELETE"])
def remove_member():
    data = request.get_json() or {}
    m = ProjectMember.query.filter_by(
        project_id=data.get("project_id"),
        user_id=data.get("user_id")
    ).first()
    if not m:
        return jsonify({"error": "Member not found"}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({"message": "Member removed"})
