from app.domain.type_enseignement import TypeEnseignement
from app.domain.interfaces import IChargeCalculator
from app.repositories.interfaces import IRepository


class UEService:
    """Cas d'usage liés aux UE : CRUD, calcul des groupes/charges, et
    disponibilité des groupes pour piloter une répartition sans conflit.

    Ne dépend que d'abstractions (IRepository, IChargeCalculator) —
    Dependency Inversion."""

    def __init__(self, ue_repository: IRepository, charge_calculator: IChargeCalculator):
        self._repo = ue_repository
        self._charge_calculator = charge_calculator

    def list_ues(self, formation_id=None):
        ues = self._repo.get_all()
        if formation_id:
            ues = [u for u in ues if u.formation_id == int(formation_id)]
        return ues

    def list_semestres(self):
        return sorted({u.semestre for u in self._repo.get_all()})

    def get_ue(self, ue_id):
        return self._repo.get_by_id(ue_id)

    def create_ue(self, data: dict):
        from app.models.unite_enseignement import UniteEnseignement

        ue = UniteEnseignement(**data)
        return self._repo.add(ue)

    def update_ue(self, ue_id, data: dict):
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return None
        for key, value in data.items():
            if hasattr(ue, key) and key != "id":
                setattr(ue, key, value)
        self._repo.save()
        return ue

    def delete_ue(self, ue_id) -> bool:
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return False
        self._repo.delete(ue)
        return True

    def get_groupes(self, ue_id):
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return None
        groupes = self._charge_calculator.compute_groups_for_ue(ue)
        return {t.value: n for t, n in groupes.items()}

    def get_charge_detail(self, ue_id):
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return None
        detail = self._charge_calculator.compute_ue_charge_detail(ue)
        result = {t.value: v for t, v in detail.items()}
        result["total"] = sum(v["charge"] for v in detail.values())
        return result

    def get_disponibilite(self, ue_id, type_enseignement: str):
        """Décrit, groupe par groupe, ce qui est déjà attribué :
        - TD / TP : chaque groupe est libre ou occupé par un enseignant.
        - CM : chaque groupe indique les heures déjà réparties et le
          reliquat disponible pour un enseignant supplémentaire.
        """
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return None
        if type_enseignement not in ("CM", "TD", "TP", "TPE"):
            return None

        t = TypeEnseignement(type_enseignement)
        ng = self._charge_calculator.compute_groups_for_ue(ue)[t]
        volume = {
            "CM": ue.volume_cm, "TD": ue.volume_td, "TP": ue.volume_tp, "TPE": ue.volume_tpe,
        }[type_enseignement]
        interventions_type = [i for i in ue.interventions if i.type_enseignement == type_enseignement]

        groupes = []
        for n in range(1, ng + 1):
            assignations = [i for i in interventions_type if i.groupe_numero == n]
            if type_enseignement == "CM":
                heures_attribuees = round(sum((i.heures or 0) for i in assignations), 2)
                groupes.append({
                    "groupe_numero": n,
                    "heures_totales": volume,
                    "heures_attribuees": heures_attribuees,
                    "heures_restantes": round(volume - heures_attribuees, 2),
                    "attributions": [
                        {"enseignant_id": i.enseignant_id, "heures": i.heures} for i in assignations
                    ],
                })
            else:
                occupe = assignations[0] if assignations else None
                groupes.append({
                    "groupe_numero": n,
                    "heures_totales": volume,
                    "libre": occupe is None,
                    "enseignant_id": occupe.enseignant_id if occupe else None,
                })

        return {"type": type_enseignement, "nombre_groupes": ng, "heures_par_groupe": volume, "groupes": groupes}

    def get_etat_complet(self, ue_id):
        """Vue d'ensemble d'une UE pour l'écran de détail : groupes
        calculés, charge totale et disponibilité par type."""
        ue = self._repo.get_by_id(ue_id)
        if not ue:
            return None
        result = {}
        for type_enseignement in ("CM", "TD", "TP", "TPE"):
            result[type_enseignement] = self.get_disponibilite(ue_id, type_enseignement)
        result["total"] = self.get_charge_detail(ue_id)["total"]
        return result
