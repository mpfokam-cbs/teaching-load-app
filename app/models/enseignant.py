from app.extensions import db


class Enseignant(db.Model):
    """Un enseignant du département et son volume horaire réglementaire."""

    __tablename__ = "enseignants"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(80))
    departement = db.Column(db.String(150))
    specialite = db.Column(db.String(150))
    volume_horaire_reference = db.Column(db.Float, nullable=False, default=192)

    interventions = db.relationship(
        "Intervention",
        backref="enseignant",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prenom": self.prenom,
            "grade": self.grade,
            "departement": self.departement,
            "specialite": self.specialite,
            "volume_horaire_reference": self.volume_horaire_reference,
        }
