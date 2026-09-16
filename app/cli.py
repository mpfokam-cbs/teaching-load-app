import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.formation import Formation
from app.models.unite_enseignement import UniteEnseignement
from app.models.enseignant import Enseignant
from app.models.intervention import Intervention


@click.command("seed")
@with_appcontext
def seed_command():
    """Réinitialise la base et insère des données de démonstration
    (reprend l'exemple 'Biochimie métabolique' du cahier des charges)."""
    db.drop_all()
    db.create_all()

    formation = Formation(
        faculte="Faculté des Sciences",
        departement="Biochimie",
        filiere="Licence Biochimie",
        niveau="L2",
        annee_academique="2026-2027",
    )
    db.session.add(formation)
    db.session.flush()

    ue = UniteEnseignement(
        formation_id=formation.id,
        code="BIO201",
        intitule="Biochimie métabolique",
        semestre="S3",
        credits=6,
        effectif_etudiant=120,
        volume_cm=30,
        volume_td=15,
        volume_tp=20,
        volume_tpe=10,
        capacite_cm=120,
        capacite_td=50,
        capacite_tp=25,
        capacite_tpe=25,
    )
    db.session.add(ue)
    db.session.flush()

    profs = [
        Enseignant(nom="A", prenom="Enseignant", grade="Professeur",
                   departement="Biochimie", volume_horaire_reference=192),
        Enseignant(nom="B", prenom="Enseignant", grade="Maître de conférences",
                   departement="Biochimie", volume_horaire_reference=192),
        Enseignant(nom="C", prenom="Enseignant", grade="Assistant",
                   departement="Biochimie", volume_horaire_reference=192),
        Enseignant(nom="D", prenom="Enseignant", grade="Assistant",
                   departement="Biochimie", volume_horaire_reference=192),
        Enseignant(nom="E", prenom="Enseignant", grade="Vacataire",
                   departement="Biochimie", volume_horaire_reference=192),
    ]
    db.session.add_all(profs)
    db.session.flush()

    interventions = [
        # CM : un seul groupe (120 étudiants / capacité 120), partagé entre A et B
        Intervention(ue_id=ue.id, enseignant_id=profs[0].id, type_enseignement="CM",
                     groupe_numero=1, heures=20),
        Intervention(ue_id=ue.id, enseignant_id=profs[1].id, type_enseignement="CM",
                     groupe_numero=1, heures=10),
        # TD : 3 groupes, chacun attribué à un seul enseignant
        Intervention(ue_id=ue.id, enseignant_id=profs[1].id, type_enseignement="TD", groupe_numero=1),
        Intervention(ue_id=ue.id, enseignant_id=profs[1].id, type_enseignement="TD", groupe_numero=2),
        Intervention(ue_id=ue.id, enseignant_id=profs[2].id, type_enseignement="TD", groupe_numero=3),
        # TP : 5 groupes, chacun attribué à un seul enseignant
        Intervention(ue_id=ue.id, enseignant_id=profs[3].id, type_enseignement="TP", groupe_numero=1),
        Intervention(ue_id=ue.id, enseignant_id=profs[3].id, type_enseignement="TP", groupe_numero=2),
        Intervention(ue_id=ue.id, enseignant_id=profs[3].id, type_enseignement="TP", groupe_numero=3),
        Intervention(ue_id=ue.id, enseignant_id=profs[4].id, type_enseignement="TP", groupe_numero=4),
        Intervention(ue_id=ue.id, enseignant_id=profs[4].id, type_enseignement="TP", groupe_numero=5),
        # TPE : 5 groupes également, répartis entre C et E
        Intervention(ue_id=ue.id, enseignant_id=profs[2].id, type_enseignement="TPE", groupe_numero=1),
        Intervention(ue_id=ue.id, enseignant_id=profs[2].id, type_enseignement="TPE", groupe_numero=2),
        Intervention(ue_id=ue.id, enseignant_id=profs[4].id, type_enseignement="TPE", groupe_numero=3),
    ]
    db.session.add_all(interventions)
    db.session.commit()

    click.echo("Données de démonstration insérées avec succès.")
