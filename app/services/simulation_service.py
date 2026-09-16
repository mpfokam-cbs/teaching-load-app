from app.domain.interfaces import IChargeCalculator
from app.domain.intervention_charge import compute_intervention_charge
from app.repositories.interfaces import IRepository


class SimulationService:
    """Permet de simuler un changement d'effectif sur une UE et de voir
    l'impact en cascade sur les groupes, la charge de l'UE et la charge de
    chaque enseignant concerné — sans jamais rien persister en base.

    Note : la charge déjà attribuée à un enseignant sur un groupe donné
    (TD/TP) ou une part de CM ne varie pas avec l'effectif — seul le
    nombre de groupes nécessaires change. La simulation met donc surtout
    en évidence les groupes supplémentaires à pourvoir."""

    def __init__(
        self,
        ue_repository: IRepository,
        enseignant_repository: IRepository,
        charge_calculator: IChargeCalculator,
    ):
        self._ue_repo = ue_repository
        self._enseignant_repo = enseignant_repository
        self._charge_calculator = charge_calculator

    def simulate_effectif(self, ue_id: int, nouvel_effectif: int):
        ue = self._ue_repo.get_by_id(ue_id)
        if not ue:
            return None

        effectif_initial = ue.effectif_etudiant
        # Modification en mémoire uniquement : jamais de commit ici.
        ue.effectif_etudiant = nouvel_effectif

        try:
            groupes = self._charge_calculator.compute_groups_for_ue(ue)
            charge_detail = self._charge_calculator.compute_ue_charge_detail(ue)

            enseignant_ids = {i.enseignant_id for i in ue.interventions}
            enseignants_impactes = []
            for eid in enseignant_ids:
                enseignant = self._enseignant_repo.get_by_id(eid)
                total = 0.0
                for interv in enseignant.interventions:
                    ue_de_interv = ue if interv.ue_id == ue.id else self._ue_repo.get_by_id(interv.ue_id)
                    if not ue_de_interv:
                        continue
                    total += compute_intervention_charge(interv, ue_de_interv)

                ecart = total - enseignant.volume_horaire_reference
                enseignants_impactes.append({
                    "enseignant_id": enseignant.id,
                    "nom_complet": f"{enseignant.prenom} {enseignant.nom}",
                    "nouvelle_charge_previsionnelle": round(total, 2),
                    "charge_reference": enseignant.volume_horaire_reference,
                    "ecart": round(ecart, 2),
                })

            return {
                "ue_id": ue.id,
                "effectif_initial": effectif_initial,
                "nouvel_effectif": nouvel_effectif,
                "nouveaux_groupes": {t.value: n for t, n in groupes.items()},
                "nouvelle_charge_ue": {t.value: v for t, v in charge_detail.items()},
                "charge_totale_ue": sum(v["charge"] for v in charge_detail.values()),
                "enseignants_impactes": enseignants_impactes,
            }
        finally:
            # On restaure systématiquement l'état d'origine : la simulation
            # ne doit jamais modifier durablement les données.
            ue.effectif_etudiant = effectif_initial
