from app.extensions import db


class UniteEnseignement(db.Model):
    """Une UE : effectif, volumes horaires par type et capacités de salle."""

    __tablename__ = "unites_enseignement"

    id = db.Column(db.Integer, primary_key=True)
    formation_id = db.Column(db.Integer, db.ForeignKey("formations.id"), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    intitule = db.Column(db.String(200), nullable=False)
    semestre = db.Column(db.String(10), nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=0)
    effectif_etudiant = db.Column(db.Integer, nullable=False, default=0)

    # Volume horaire de référence (par groupe) prévu à la maquette
    volume_cm = db.Column(db.Float, nullable=False, default=0)
    volume_td = db.Column(db.Float, nullable=False, default=0)
    volume_tp = db.Column(db.Float, nullable=False, default=0)
    volume_tpe = db.Column(db.Float, nullable=False, default=0)

    # Capacité d'accueil d'un groupe pour chaque type d'enseignement
    capacite_cm = db.Column(db.Integer, nullable=False, default=200)
    capacite_td = db.Column(db.Integer, nullable=False, default=50)
    capacite_tp = db.Column(db.Integer, nullable=False, default=25)
    capacite_tpe = db.Column(db.Integer, nullable=False, default=25)

    interventions = db.relationship(
        "Intervention",
        backref="unite_enseignement",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "formation_id": self.formation_id,
            "code": self.code,
            "intitule": self.intitule,
            "semestre": self.semestre,
            "credits": self.credits,
            "effectif_etudiant": self.effectif_etudiant,
            "volume_cm": self.volume_cm,
            "volume_td": self.volume_td,
            "volume_tp": self.volume_tp,
            "volume_tpe": self.volume_tpe,
            "capacite_cm": self.capacite_cm,
            "capacite_td": self.capacite_td,
            "capacite_tp": self.capacite_tp,
            "capacite_tpe": self.capacite_tpe,
        }
