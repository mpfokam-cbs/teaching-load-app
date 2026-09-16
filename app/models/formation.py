from app.extensions import db


class Formation(db.Model):
    """Une formation universitaire (faculté / département / filière / niveau)."""

    __tablename__ = "formations"

    id = db.Column(db.Integer, primary_key=True)
    faculte = db.Column(db.String(150), nullable=False)
    departement = db.Column(db.String(150), nullable=False)
    filiere = db.Column(db.String(150), nullable=False)
    niveau = db.Column(db.String(10), nullable=False)  # L1, L2, L3, M1, M2
    annee_academique = db.Column(db.String(20), nullable=False)

    unites_enseignement = db.relationship(
        "UniteEnseignement",
        backref="formation",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "faculte": self.faculte,
            "departement": self.departement,
            "filiere": self.filiere,
            "niveau": self.niveau,
            "annee_academique": self.annee_academique,
        }
