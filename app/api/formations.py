from flask import Blueprint, jsonify, request

from app.container import container
from app.models.formation import Formation

bp = Blueprint("formations", __name__, url_prefix="/api/formations")

REQUIRED_FIELDS = ["faculte", "departement", "filiere", "niveau", "annee_academique"]


@bp.get("")
def list_formations():
    formations = container.formation_repo.get_all()
    return jsonify([f.to_dict() for f in formations])


@bp.post("")
def create_formation():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if not data.get(f)]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400
    formation = Formation(**{k: data[k] for k in REQUIRED_FIELDS})
    container.formation_repo.add(formation)
    return jsonify(formation.to_dict()), 201


@bp.get("/<int:id_>")
def get_formation(id_):
    formation = container.formation_repo.get_by_id(id_)
    if not formation:
        return jsonify({"error": "Formation introuvable"}), 404
    return jsonify(formation.to_dict())


@bp.put("/<int:id_>")
def update_formation(id_):
    formation = container.formation_repo.get_by_id(id_)
    if not formation:
        return jsonify({"error": "Formation introuvable"}), 404
    data = request.get_json(silent=True) or {}
    for key in REQUIRED_FIELDS:
        if key in data:
            setattr(formation, key, data[key])
    container.formation_repo.save()
    return jsonify(formation.to_dict())


@bp.delete("/<int:id_>")
def delete_formation(id_):
    formation = container.formation_repo.get_by_id(id_)
    if not formation:
        return jsonify({"error": "Formation introuvable"}), 404
    container.formation_repo.delete(formation)
    return "", 204
