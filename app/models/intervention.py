from app.extensions import db


class Intervention(db.Model):
    """Affectation d'un enseignant sur un groupe précis d'un type
    d'enseignement d'une UE.

    - Pour TD et TP : un groupe (identifié par ``groupe_numero``) ne peut
      être attribué qu'à UN SEUL enseignant. Il prend alors la totalité
      des heures de ce groupe.
    - Pour CM : il n'y a en général qu'un seul groupe, mais plusieurs
      enseignants peuvent s'y partager les heures. ``heures`` indique
      alors la part que prend cet enseignant.
    """

    __tablename__ = "interventions"

    id = db.Column(db.Integer, primary_key=True)
    ue_id = db.Column(db.Integer, db.ForeignKey("unites_enseignement.id"), nullable=False)
    enseignant_id = db.Column(db.Integer, db.ForeignKey("enseignants.id"), nullable=False)
    type_enseignement = db.Column(db.String(5), nullable=False)  # "CM", "TD" ou "TP"
    groupe_numero = db.Column(db.Integer, nullable=False, default=1)
    heures = db.Column(db.Float, nullable=True)  # renseigné uniquement pour le CM

    def to_dict(self):
        return {
            "id": self.id,
            "ue_id": self.ue_id,
            "enseignant_id": self.enseignant_id,
            "type_enseignement": self.type_enseignement,
            "groupe_numero": self.groupe_numero,
            "heures": self.heures,
        }
