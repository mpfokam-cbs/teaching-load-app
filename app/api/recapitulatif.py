from flask import Blueprint, jsonify, request

from app.container import container

bp = Blueprint("recapitulatif", __name__, url_prefix="/api/recapitulatif")


@bp.get("")
def recapitulatif():
    semestre = request.args.get("semestre") or None
    return jsonify(container.enseignant_service.recapitulatif(semestre))
