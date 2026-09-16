import math

from app.domain.interfaces import IGroupCalculator, IChargeCalculator
from app.domain.type_enseignement import TypeEnseignement


class GroupCalculator(IGroupCalculator):
    """Calcule Ng = ceil(effectif / capacite) — Single Responsibility :
    cette classe ne fait qu'une chose, calculer un nombre de groupes."""

    def compute_groups(self, effectif: int, capacite: int) -> int:
        if capacite is None or capacite <= 0:
            raise ValueError("La capacité d'accueil doit être un entier positif")
        if effectif is None or effectif <= 0:
            return 0
        return math.ceil(effectif / capacite)


class ChargeCalculator(IChargeCalculator):
    """Calcule la charge horaire réelle générée par une UE, pour les
    quatre types d'enseignement (CM, TD, TP, TPE).

    Dépend d'un IGroupCalculator injecté (Dependency Inversion) plutôt que
    d'une classe concrète : on peut substituer n'importe quelle autre
    implémentation de IGroupCalculator sans modifier cette classe."""

    def __init__(self, group_calculator: IGroupCalculator):
        self._group_calculator = group_calculator

    def compute_groups_for_ue(self, ue) -> dict:
        return {
            TypeEnseignement.CM: self._group_calculator.compute_groups(
                ue.effectif_etudiant, ue.capacite_cm
            ),
            TypeEnseignement.TD: self._group_calculator.compute_groups(
                ue.effectif_etudiant, ue.capacite_td
            ),
            TypeEnseignement.TP: self._group_calculator.compute_groups(
                ue.effectif_etudiant, ue.capacite_tp
            ),
            TypeEnseignement.TPE: self._group_calculator.compute_groups(
                ue.effectif_etudiant, ue.capacite_tpe
            ),
        }

    def compute_ue_charge_detail(self, ue) -> dict:
        groupes = self.compute_groups_for_ue(ue)
        volumes = {
            TypeEnseignement.CM: ue.volume_cm,
            TypeEnseignement.TD: ue.volume_td,
            TypeEnseignement.TP: ue.volume_tp,
            TypeEnseignement.TPE: ue.volume_tpe,
        }
        detail = {}
        for t in TypeEnseignement:
            n = groupes[t]
            h = volumes[t]
            detail[t] = {"groupes": n, "heures_par_groupe": h, "charge": n * h}
        return detail

    def compute_ue_total_charge(self, ue) -> float:
        detail = self.compute_ue_charge_detail(ue)
        return sum(v["charge"] for v in detail.values())
