from flask import Blueprint, jsonify, request

from app.container import container

bp = Blueprint("ues", __name__, url_prefix="/api/ues")

REQUIRED_FIELDS = [
    "formation_id",
    "code",
    "intitule",
    "semestre",
    "effectif_etudiant",
    "volume_cm",
    "volume_td",
    "volume_tp",
    "volume_tpe",
]


@bp.get("")
def list_ues():
    formation_id = request.args.get("formation_id")
    ues = container.ue_service.list_ues(formation_id)
    return jsonify([u.to_dict() for u in ues])


@bp.post("")
def create_ue():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400
    if not container.formation_repo.get_by_id(data["formation_id"]):
        return jsonify({"error": "Formation introuvable"}), 404
    try:
        ue = container.ue_service.create_ue(data)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(ue.to_dict()), 201


@bp.get("/<int:id_>")
def get_ue(id_):
    ue = container.ue_service.get_ue(id_)
    if not ue:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(ue.to_dict())


@bp.put("/<int:id_>")
def update_ue(id_):
    data = request.get_json(silent=True) or {}
    ue = container.ue_service.update_ue(id_, data)
    if not ue:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(ue.to_dict())


@bp.delete("/<int:id_>")
def delete_ue(id_):
    if not container.ue_service.delete_ue(id_):
        return jsonify({"error": "UE introuvable"}), 404
    return "", 204


@bp.get("/<int:id_>/groupes")
def get_groupes(id_):
    result = container.ue_service.get_groupes(id_)
    if result is None:
        return jsonify({"error": "UE introuvable"}), 404
    assignes = container.ue_service.get_groupes_assignes(id_)
    return jsonify({"groupes_calcules": result, "groupes_assignes": assignes})


@bp.get("/<int:id_>/charge")
def get_charge(id_):
    result = container.ue_service.get_charge_detail(id_)
    if result is None:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(result)


@bp.get("/<int:id_>/disponibilite")
def get_disponibilite(id_):
    type_enseignement = request.args.get("type")
    if type_enseignement not in ("CM", "TD", "TP", "TPE"):
        return jsonify({"error": "Le paramètre type doit être CM, TD, TP ou TPE"}), 400
    result = container.ue_service.get_disponibilite(id_, type_enseignement)
    if result is None:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(result)


@bp.get("/<int:id_>/etat")
def get_etat(id_):
    result = container.ue_service.get_etat_complet(id_)
    if result is None:
        return jsonify({"error": "UE introuvable"}), 404
    return jsonify(result)


@bp.get("/semestres")
def list_semestres():
    return jsonify(container.ue_service.list_semestres())
