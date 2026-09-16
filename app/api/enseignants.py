from flask import Blueprint, jsonify, request

from app.container import container

bp = Blueprint("enseignants", __name__, url_prefix="/api/enseignants")

REQUIRED_FIELDS = ["nom", "prenom"]


@bp.get("")
def list_enseignants():
    items = container.enseignant_service.list_enseignants()
    return jsonify([e.to_dict() for e in items])


@bp.post("")
def create_enseignant():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400
    data.setdefault("volume_horaire_reference", 192)
    e = container.enseignant_service.create_enseignant(data)
    return jsonify(e.to_dict()), 201


@bp.get("/<int:id_>")
def get_enseignant(id_):
    e = container.enseignant_service.get_enseignant(id_)
    if not e:
        return jsonify({"error": "Enseignant introuvable"}), 404
    return jsonify(e.to_dict())


@bp.put("/<int:id_>")
def update_enseignant(id_):
    data = request.get_json(silent=True) or {}
    e = container.enseignant_service.update_enseignant(id_, data)
    if not e:
        return jsonify({"error": "Enseignant introuvable"}), 404
    return jsonify(e.to_dict())


@bp.delete("/<int:id_>")
def delete_enseignant(id_):
    if not container.enseignant_service.delete_enseignant(id_):
        return jsonify({"error": "Enseignant introuvable"}), 404
    return "", 204


@bp.get("/<int:id_>/charge")
def get_charge(id_):
    result = container.enseignant_service.compute_charge(id_)
    if result is None:
        return jsonify({"error": "Enseignant introuvable"}), 404
    return jsonify(result)
