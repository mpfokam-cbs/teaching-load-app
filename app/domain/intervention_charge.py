"""Règle métier : quelle charge horaire imputer à une intervention donnée.

Isolée ici (Single Responsibility) car elle est utilisée à la fois par
EnseignantService et SimulationService — DRY plutôt que dupliquée."""


def compute_intervention_charge(intervention, ue) -> float:
    """
    - CM : un seul groupe en général, mais les heures peuvent être
      partagées entre plusieurs enseignants → on retient la part
      explicitement saisie pour cet enseignant (``intervention.heures``).
    - TD / TP / TPE : chaque groupe est attribué à un seul enseignant, qui
      prend donc la totalité des heures du groupe.
    """
    if intervention.type_enseignement == "CM":
        return intervention.heures or 0.0
    volumes = {"TD": ue.volume_td, "TP": ue.volume_tp, "TPE": ue.volume_tpe}
    return volumes[intervention.type_enseignement]
