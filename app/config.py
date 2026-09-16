import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _normalise_database_url(url: str) -> str:
    """Certains fournisseurs (Render, Heroku...) donnent une URL qui
    commence par 'postgres://', alors que SQLAlchemy 2.x exige le
    préfixe 'postgresql://'. On corrige automatiquement si besoin."""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    _database_url = os.environ.get("DATABASE_URL")
    if _database_url:
        SQLALCHEMY_DATABASE_URI = _normalise_database_url(_database_url)
    else:
        # Par défaut (développement local) : base SQLite dans le projet.
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'teaching_load.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
