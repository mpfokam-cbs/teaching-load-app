from flask import Blueprint, jsonify, request

from app.container import container

bp = Blueprint("interventions", __name__, url_prefix="/api/interventions")


@bp.get("")
def list_interventions():
    ue_id = request.args.get("ue_id")
    enseignant_id = request.args.get("enseignant_id")
    items = container.intervention_service.list_interventions(ue_id, enseignant_id)
    return jsonify([i.to_dict() for i in items])


@bp.post("")
def create_intervention():
    data = request.get_json(silent=True) or {}
    required = ["ue_id", "enseignant_id", "type_enseignement", "groupe_numero"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400
    if data.get("type_enseignement") == "CM" and data.get("heures") in (None, ""):
        return jsonify({"error": "Champs manquants : heures"}), 400
    try:
        interv = container.intervention_service.create_intervention(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(interv.to_dict()), 201


@bp.delete("/<int:id_>")
def delete_intervention(id_):
    if not container.intervention_service.delete_intervention(id_):
        return jsonify({"error": "Intervention introuvable"}), 404
    return "", 204
