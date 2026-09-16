from app.extensions import db
from app.models.formation import Formation
from app.models.unite_enseignement import UniteEnseignement
from app.models.enseignant import Enseignant
from app.models.intervention import Intervention
from app.repositories.interfaces import IRepository


class SQLAlchemyRepository(IRepository):
    """Implémentation générique basée sur SQLAlchemy. Chaque sous-classe ne
    fait que déclarer le modèle concerné (Single Responsibility / DRY)."""

    model = None

    def get_all(self):
        return self.model.query.all()

    def get_by_id(self, id_):
        return self.model.query.get(id_)

    def add(self, entity):
        db.session.add(entity)
        self.save()
        return entity

    def delete(self, entity):
        db.session.delete(entity)
        self.save()

    def save(self):
        db.session.commit()


class FormationRepository(SQLAlchemyRepository):
    model = Formation


class UniteEnseignementRepository(SQLAlchemyRepository):
    model = UniteEnseignement


class EnseignantRepository(SQLAlchemyRepository):
    model = Enseignant


class InterventionRepository(SQLAlchemyRepository):
    model = Intervention
