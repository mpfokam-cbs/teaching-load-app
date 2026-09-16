from abc import ABC, abstractmethod


class IGroupCalculator(ABC):
    """Abstraction du calcul du nombre de groupes (Interface Segregation :
    ne contient que ce dont un calcul de groupes a besoin)."""

    @abstractmethod
    def compute_groups(self, effectif: int, capacite: int) -> int:
        ...


class IChargeCalculator(ABC):
    """Abstraction du calcul de la charge horaire d'une UE.

    Les services applicatifs dépendent de cette interface (Dependency
    Inversion) et non d'une implémentation concrète : on pourrait ainsi
    remplacer la stratégie de calcul sans toucher au reste du code
    (Open/Closed)."""

    @abstractmethod
    def compute_groups_for_ue(self, ue) -> dict:
        ...

    @abstractmethod
    def compute_ue_charge_detail(self, ue) -> dict:
        ...

    @abstractmethod
    def compute_ue_total_charge(self, ue) -> float:
        ...
