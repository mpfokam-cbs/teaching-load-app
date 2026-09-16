from enum import Enum


class TypeEnseignement(str, Enum):
    """Les quatre formes d'intervention possibles sur une UE."""

    CM = "CM"
    TD = "TD"
    TP = "TP"
    TPE = "TPE"
