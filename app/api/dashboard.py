from flask import Blueprint, jsonify

from app.container import container

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
def dashboard():
    """Détail de la charge de chaque enseignant, UE par UE."""
    return jsonify(container.enseignant_service.dashboard_detaille())
