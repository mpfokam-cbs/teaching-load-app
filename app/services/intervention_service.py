from app.domain.type_enseignement import TypeEnseignement
from app.domain.interfaces import IChargeCalculator
from app.repositories.interfaces import IRepository

TYPES_VALIDES = ("CM", "TD", "TP", "TPE")
TOLERANCE = 1e-6


class InterventionService:
    """Cas d'usage liés à la répartition de la charge entre enseignants.

    Applique les deux règles métier demandées :
    - CM : un seul groupe, mais ses heures peuvent être partagées entre
      plusieurs enseignants (la somme des parts ne doit pas dépasser le
      volume horaire du groupe).
    - TD / TP : chaque groupe est attribué à un seul enseignant ; deux
      enseignants ne peuvent jamais se voir attribuer le même groupe.
    """

    def __init__(
        self,
        intervention_repository: IRepository,
        ue_repository: IRepository,
        enseignant_repository: IRepository,
        charge_calculator: IChargeCalculator,
    ):
        self._repo = intervention_repository
        self._ue_repo = ue_repository
        self._enseignant_repo = enseignant_repository
        self._charge_calculator = charge_calculator

    def list_interventions(self, ue_id=None, enseignant_id=None):
        items = self._repo.get_all()
        if ue_id:
            items = [i for i in items if i.ue_id == int(ue_id)]
        if enseignant_id:
            items = [i for i in items if i.enseignant_id == int(enseignant_id)]
        return items

    def create_intervention(self, data: dict):
        from app.models.intervention import Intervention

        type_enseignement = data.get("type_enseignement")
        if type_enseignement not in TYPES_VALIDES:
            raise ValueError("type_enseignement doit être CM, TD, TP ou TPE")

        ue = self._ue_repo.get_by_id(data.get("ue_id"))
        if not ue:
            raise ValueError("UE introuvable")
        if not self._enseignant_repo.get_by_id(data.get("enseignant_id")):
            raise ValueError("Enseignant introuvable")

        groupe_numero = int(data.get("groupe_numero", 1))
        nb_groupes = self._charge_calculator.compute_groups_for_ue(ue)[TypeEnseignement(type_enseignement)]
        if nb_groupes == 0:
            raise ValueError(f"Aucun groupe de {type_enseignement} n'est nécessaire pour cette UE (effectif nul)")
        if not (1 <= groupe_numero <= nb_groupes):
            raise ValueError(f"Le numéro de groupe {type_enseignement} doit être compris entre 1 et {nb_groupes}")

        existants = [
            i for i in ue.interventions
            if i.type_enseignement == type_enseignement and i.groupe_numero == groupe_numero
        ]

        if type_enseignement == "CM":
            heures = data.get("heures")
            if heures in (None, ""):
                raise ValueError("Le nombre d'heures est requis pour une intervention en CM")
            heures = float(heures)
            if heures <= 0:
                raise ValueError("Le nombre d'heures doit être positif")
            deja_attribuees = sum((i.heures or 0) for i in existants)
            restant = ue.volume_cm - deja_attribuees
            if heures > restant + TOLERANCE:
                raise ValueError(
                    f"Il ne reste que {round(restant, 2)}h disponibles sur ce groupe de CM "
                    f"(sur {ue.volume_cm}h au total)"
                )
        else:
            heures = None
            if existants:
                raise ValueError(
                    f"Le groupe {type_enseignement} n°{groupe_numero} est déjà attribué à un autre enseignant"
                )

        interv = Intervention(
            ue_id=ue.id,
            enseignant_id=data["enseignant_id"],
            type_enseignement=type_enseignement,
            groupe_numero=groupe_numero,
            heures=heures,
        )
        return self._repo.add(interv)

    def delete_intervention(self, id_) -> bool:
        interv = self._repo.get_by_id(id_)
        if not interv:
            return False
        self._repo.delete(interv)
        return True
