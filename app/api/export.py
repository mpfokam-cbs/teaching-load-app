from flask import Blueprint, send_file

from app.container import container

bp = Blueprint("export", __name__, url_prefix="/api/export")


@bp.get("/enseignants")
def export_enseignants():
    buffer = container.export_service.build_workbook()
    return send_file(
        buffer,
        as_attachment=True,
        download_name="charges_enseignants.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
