from flask import Blueprint, request, jsonify, current_app
from ..services.sync_service import SyncService

webhooks_bp = Blueprint("webhooks", __name__)
sync_svc = SyncService()


@webhooks_bp.route("/github", methods=["POST"])
def github_webhook():
    delivery_id = request.headers.get("X-GitHub-Delivery", "")
    event_type = request.headers.get("X-GitHub-Event", "")
    signature = request.headers.get("X-Hub-Signature-256", "")

    if current_app.config.get("GITHUB_WEBHOOK_SECRET"):
        if not sync_svc.verify_signature(request.data, signature):
            return jsonify({"error": "Invalid webhook signature"}), 403

    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    if not payload:
        return jsonify({"error": "Empty payload"}), 400

    result = sync_svc.handle_event(delivery_id, event_type, payload)
    return jsonify(result)


@webhooks_bp.route("/test", methods=["POST"])
def test_webhook():
    """Endpoint to test webhook connectivity."""
    return jsonify({"status": "ok", "message": "TeamSync webhook endpoint is active"})
