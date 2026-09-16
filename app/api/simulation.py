from flask import Blueprint, jsonify, request

from app.container import container

bp = Blueprint("simulation", __name__, url_prefix="/api/simulation")


@bp.post("")
def simulate():
    data = request.get_json(silent=True) or {}
    ue_id = data.get("ue_id")
    nouvel_effectif = data.get("nouvel_effectif")
    if ue_id is None or nouvel_effectif is None:
        return jsonify({"error": "ue_id et nouvel_effectif sont requis"}), 400
    result = container.simulation_service.simulate_effectif(int(ue_id), int(nouvel_effectif))
    if result is None:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(result)
