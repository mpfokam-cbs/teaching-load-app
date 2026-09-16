from flask import Flask, render_template
from flask_cors import CORS

from app.config import Config
from app.extensions import db


def create_app(config_class=Config):
    """Application factory : compose l'app Flask et branche chaque couche."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)

    # --- Enregistrement des blueprints (API REST) ---
    from app.api.formations import bp as formations_bp
    from app.api.ues import bp as ues_bp
    from app.api.enseignants import bp as enseignants_bp
    from app.api.interventions import bp as interventions_bp
    from app.api.simulation import bp as simulation_bp
    from app.api.dashboard import bp as dashboard_bp
    from app.api.recapitulatif import bp as recapitulatif_bp
    from app.api.export import bp as export_bp

    app.register_blueprint(formations_bp)
    app.register_blueprint(ues_bp)
    app.register_blueprint(enseignants_bp)
    app.register_blueprint(interventions_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(recapitulatif_bp)
    app.register_blueprint(export_bp)

    # --- Commandes CLI (ex : flask --app run.py seed) ---
    from app.cli import seed_command
    app.cli.add_command(seed_command)

    @app.route("/")
    def index():
        return render_template("index.html")

    with app.app_context():
        db.create_all()

    return app
