"""Racine de composition de l'application.

C'est le SEUL endroit du code qui relie des implémentations concrètes
(SQLAlchemy, calculateurs) à des abstractions. Tout le reste du code
(services, routes) ne connaît que des interfaces — c'est ce qui permet de
respecter le principe d'inversion des dépendances (DIP)."""

from app.repositories.sqlalchemy_repositories import (
    FormationRepository,
    UniteEnseignementRepository,
    EnseignantRepository,
    InterventionRepository,
)
from app.domain.calculators import GroupCalculator, ChargeCalculator
from app.services.ue_service import UEService
from app.services.enseignant_service import EnseignantService
from app.services.intervention_service import InterventionService
from app.services.simulation_service import SimulationService
from app.services.export_service import ExportService


class Container:
    def __init__(self):
        # Dépôts (accès aux données)
        self.formation_repo = FormationRepository()
        self.ue_repo = UniteEnseignementRepository()
        self.enseignant_repo = EnseignantRepository()
        self.intervention_repo = InterventionRepository()

        # Domaine (règles de calcul)
        self.group_calculator = GroupCalculator()
        self.charge_calculator = ChargeCalculator(self.group_calculator)

        # Services applicatifs (injectés avec des abstractions)
        self.ue_service = UEService(self.ue_repo, self.charge_calculator)
        self.enseignant_service = EnseignantService(self.enseignant_repo, self.ue_repo)
        self.intervention_service = InterventionService(
            self.intervention_repo, self.ue_repo, self.enseignant_repo, self.charge_calculator
        )
        self.simulation_service = SimulationService(
            self.ue_repo, self.enseignant_repo, self.charge_calculator
        )
        self.export_service = ExportService(self.enseignant_repo, self.ue_repo)


container = Container()
