from abc import ABC, abstractmethod


class IRepository(ABC):
    """Abstraction d'accès aux données. Les services métier dépendent de
    cette interface, jamais de SQLAlchemy directement : on pourrait donc
    remplacer la persistance (ex : dépôt en mémoire pour les tests) sans
    changer une ligne de la logique métier (Dependency Inversion,
    Liskov Substitution)."""

    @abstractmethod
    def get_all(self):
        ...

    @abstractmethod
    def get_by_id(self, id_):
        ...

    @abstractmethod
    def add(self, entity):
        ...

    @abstractmethod
    def delete(self, entity):
        ...

    @abstractmethod
    def save(self):
        ...
