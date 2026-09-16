from app.domain.intervention_charge import compute_intervention_charge
from app.repositories.interfaces import IRepository


def _statut(ecart: float) -> str:
    if abs(ecart) <= 1e-9:
        return "equilibre"
    return "surcharge" if ecart > 0 else "inferieur"


class EnseignantService:
    """Cas d'usage liés aux enseignants : CRUD + agrégation de la charge
    prévisionnelle à partir des interventions (Single Responsibility)."""

    def __init__(self, enseignant_repository: IRepository, ue_repository: IRepository):
        self._repo = enseignant_repository
        self._ue_repo = ue_repository

    # ---------- CRUD ----------
    def list_enseignants(self):
        return self._repo.get_all()

    def get_enseignant(self, id_):
        return self._repo.get_by_id(id_)

    def create_enseignant(self, data: dict):
        from app.models.enseignant import Enseignant

        e = Enseignant(**data)
        return self._repo.add(e)

    def update_enseignant(self, id_, data: dict):
        e = self._repo.get_by_id(id_)
        if not e:
            return None
        for key, value in data.items():
            if hasattr(e, key) and key != "id":
                setattr(e, key, value)
        self._repo.save()
        return e

    def delete_enseignant(self, id_) -> bool:
        e = self._repo.get_by_id(id_)
        if not e:
            return False
        self._repo.delete(e)
        return True

    # ---------- Charge ----------
    def compute_charge(self, enseignant_id):
        """Détail intervention par intervention (utilisé pour la fiche
        individuelle d'un enseignant)."""
        e = self._repo.get_by_id(enseignant_id)
        if not e:
            return None

        detail = []
        total = 0.0
        for interv in e.interventions:
            ue = self._ue_repo.get_by_id(interv.ue_id)
            if not ue:
                continue
            charge = compute_intervention_charge(interv, ue)
            total += charge
            detail.append({
                "ue_id": ue.id,
                "ue_code": ue.code,
                "ue_intitule": ue.intitule,
                "type_enseignement": interv.type_enseignement,
                "groupe_numero": interv.groupe_numero,
                "heures": round(charge, 2),
            })

        ecart = total - e.volume_horaire_reference
        return {
            "enseignant": e.to_dict(),
            "detail": detail,
            "charge_previsionnelle": round(total, 2),
            "charge_reference": e.volume_horaire_reference,
            "ecart": round(ecart, 2),
            "statut": _statut(ecart),
        }

    def charge_par_ue(self, enseignant_id):
        """Regroupe la charge de l'enseignant par UE : heures de CM,
        nombre de groupes + heures pour TD et TP, total par UE et total
        général — c'est la structure attendue par l'onglet Tableau de bord."""
        e = self._repo.get_by_id(enseignant_id)
        if not e:
            return None

        par_ue = {}
        for interv in e.interventions:
            ue = self._ue_repo.get_by_id(interv.ue_id)
            if not ue:
                continue
            entry = par_ue.setdefault(ue.id, {
                "ue_id": ue.id,
                "ue_code": ue.code,
                "ue_intitule": ue.intitule,
                "semestre": ue.semestre,
                "cm_heures": 0.0,
                "td_groupes": 0,
                "td_heures": 0.0,
                "tp_groupes": 0,
                "tp_heures": 0.0,
                "tpe_groupes": 0,
                "tpe_heures": 0.0,
            })
            charge = compute_intervention_charge(interv, ue)
            if interv.type_enseignement == "CM":
                entry["cm_heures"] += charge
            elif interv.type_enseignement == "TD":
                entry["td_groupes"] += 1
                entry["td_heures"] += charge
            elif interv.type_enseignement == "TP":
                entry["tp_groupes"] += 1
                entry["tp_heures"] += charge
            else:
                entry["tpe_groupes"] += 1
                entry["tpe_heures"] += charge

        lignes = []
        total_general = 0.0
        for entry in sorted(par_ue.values(), key=lambda x: x["ue_code"]):
            total_ue = entry["cm_heures"] + entry["td_heures"] + entry["tp_heures"] + entry["tpe_heures"]
            entry["cm_heures"] = round(entry["cm_heures"], 2)
            entry["td_heures"] = round(entry["td_heures"], 2)
            entry["tp_heures"] = round(entry["tp_heures"], 2)
            entry["tpe_heures"] = round(entry["tpe_heures"], 2)
            entry["total_ue"] = round(total_ue, 2)
            total_general += total_ue
            lignes.append(entry)

        ecart = total_general - e.volume_horaire_reference
        return {
            "enseignant": e.to_dict(),
            "lignes": lignes,
            "total_general": round(total_general, 2),
            "charge_reference": e.volume_horaire_reference,
            "ecart": round(ecart, 2),
            "statut": _statut(ecart),
        }

    def dashboard_detaille(self):
        """Détail par UE de tous les enseignants — alimente l'onglet
        Tableau de bord."""
        return [self.charge_par_ue(e.id) for e in self._repo.get_all()]

    def recapitulatif(self, semestre=None):
        """Charge totale de chaque enseignant, éventuellement restreinte à
        un semestre — alimente l'onglet Récapitulatif (fin de semestre ou
        d'année, selon que l'on filtre ou non)."""
        resultats = []
        for e in self._repo.get_all():
            total = 0.0
            for interv in e.interventions:
                ue = self._ue_repo.get_by_id(interv.ue_id)
                if not ue:
                    continue
                if semestre and ue.semestre != semestre:
                    continue
                total += compute_intervention_charge(interv, ue)
            ecart = total - e.volume_horaire_reference
            resultats.append({
                "enseignant": e.to_dict(),
                "charge_previsionnelle": round(total, 2),
                "charge_reference": e.volume_horaire_reference,
                "ecart": round(ecart, 2),
                "statut": _statut(ecart),
            })
        return resultats
