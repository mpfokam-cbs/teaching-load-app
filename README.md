# Registre des charges d'enseignement

Application Flask (backend + frontend) pour calculer, à partir des effectifs
étudiants, le nombre de groupes de CM/TD/TP, la charge horaire de chaque
unité d'enseignement (UE), puis la charge prévisionnelle de chaque
enseignant — avec comparaison au volume horaire réglementaire et simulation
de scénarios (« que se passe-t-il si l'effectif change ? »).

## Installation

```bash
cd teaching_load_app
python3 -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'application

```bash
export FLASK_APP=run.py           # Windows : set FLASK_APP=run.py
flask seed                        # optionnel : insère un exemple de démonstration
flask run
```

Ouvrir ensuite http://127.0.0.1:5000 dans un navigateur.

La commande `flask seed` réinitialise la base SQLite (`teaching_load.db`) et
insère l'exemple « Biochimie métabolique » (120 étudiants, 5 enseignants)
utilisé dans le cahier des charges, pour tester l'application immédiatement.

> **Mise à jour depuis une version antérieure** : si vous aviez déjà un
> fichier `teaching_load.db` créé avant l'ajout du TPE, supprimez-le (ou
> relancez `flask seed`) avant de redémarrer l'application, car de
> nouvelles colonnes ont été ajoutées au modèle des UE.

## Architecture (principes SOLID)

```
app/
  models/        Persistance (SQLAlchemy) : Formation, UniteEnseignement,
                 Enseignant, Intervention
  domain/        Règles métier pures, sans dépendance à Flask/SQLAlchemy :
                 - type_enseignement.py   : énumération CM / TD / TP
                 - interfaces.py          : IGroupCalculator, IChargeCalculator
                 - calculators.py         : GroupCalculator, ChargeCalculator
  repositories/  Accès aux données derrière une interface IRepository,
                 avec une implémentation SQLAlchemy
  services/      Cas d'usage applicatifs (UEService, EnseignantService,
                 InterventionService, SimulationService), qui ne dépendent
                 que d'abstractions (repositories/calculateurs injectés)
  api/           Blueprints Flask exposant les services en JSON
  container.py   Racine de composition : relie les implémentations
                 concrètes aux abstractions (injection de dépendances)
  templates/, static/   Frontend HTML/CSS/JS (aucune dépendance externe)
```

Application des cinq principes SOLID :

- **S**ingle Responsibility — chaque classe a un seul rôle : `GroupCalculator`
  ne fait que calculer un nombre de groupes, `ChargeCalculator` ne fait que
  calculer une charge, chaque repository ne gère qu'un seul modèle.
- **O**pen/Closed — `ChargeCalculator` dépend de l'abstraction
  `IGroupCalculator` : on peut changer la règle de calcul des groupes
  (ex. arrondi différent, capacités variables selon le semestre) en créant
  une nouvelle implémentation, sans modifier `ChargeCalculator`.
- **L**iskov Substitution — toute implémentation de `IRepository` (SQLAlchemy
  ou une autre, ex. en mémoire pour les tests) peut remplacer une autre sans
  changer le comportement attendu par les services.
- **I**nterface Segregation — les interfaces (`IGroupCalculator`,
  `IChargeCalculator`, `IRepository`) sont volontairement étroites : chacune
  n'expose que ce dont ses utilisateurs ont besoin.
- **D**ependency Inversion — les services (`UEService`, `EnseignantService`,
  `SimulationService`…) ne dépendent que d'abstractions ; les implémentations
  concrètes sont assemblées une seule fois, dans `container.py`.

## Logique métier

1. **Nombre de groupes** : `Ng = ceil(effectif / capacité)`, calculé
   séparément pour CM, TD et TP (capacités configurables par UE).
2. **Répartition entre enseignants** — deux règles différentes selon le type :
   - **CM** : il n'y a en général qu'un seul groupe, mais plusieurs
     enseignants peuvent s'en partager les heures (ex. 20h pour l'un, 10h
     pour l'autre sur un total de 30h). La somme des heures attribuées à un
     groupe de CM ne peut jamais dépasser son volume horaire total.
   - **TD / TP** : chaque groupe est attribué à un seul enseignant, qui en
     prend la totalité des heures. Deux enseignants ne peuvent jamais se
     voir attribuer le même groupe (l'application refuse la création d'une
     intervention en conflit).
3. **Charge d'un enseignant** : somme des charges de toutes ses
   interventions (heures de CM prises + heures des groupes de TD/TP qui lui
   sont attribués), toutes UE confondues.
4. **Comparaison au référentiel** : écart entre charge prévisionnelle et
   volume horaire réglementaire de l'enseignant, avec statut (équilibrée /
   inférieure / en surcharge).
5. **Simulation** : rejoue les calculs 1 à 4 pour un nouvel effectif d'UE
   (nouveaux groupes nécessaires, nouvelle charge), sans jamais modifier les
   données enregistrées.

## Onglets de l'application

- **Formations / UE / Enseignants** : gestion des données de base, avec
  possibilité de **modifier** une UE ou un enseignant existant (bouton
  « Modifier » dans chaque tableau).
- **Répartition** : affecter un enseignant à un ou plusieurs groupes. Pour
  le CM, un seul groupe à la fois avec partage d'heures ; pour TD, TP et
  **TPE**, on peut cocher plusieurs groupes disponibles en une seule fois
  pour le même enseignant. Chaque affectation (réussie ou non) déclenche une
  notification visuelle.
- **Tableau de bord** : détail de la charge de chaque enseignant, UE par UE
  (CM en heures, TD/TP/TPE en nombre de groupes + heures), avec le total de
  la période pour chaque enseignant, et un bouton pour **télécharger le
  tableau Excel** récapitulatif du département (15 colonnes, une ligne par
  enseignant/UE, triée par ordre alphabétique).
- **Récapitulatif** : charge totale de chaque enseignant comparée à son
  total heure dû, filtrable par semestre ou sur l'année complète.
- **Simulation** : impact d'un changement d'effectif sur les groupes
  nécessaires et la charge de l'UE.

## API REST

| Méthode | Route                                    | Description                                    |
|---------|--------------------------------------------|-------------------------------------------------|
| GET/POST | `/api/formations`                        | Lister / créer une formation                    |
| GET/PUT/DELETE | `/api/formations/<id>`             | Détail / modifier / supprimer                   |
| GET/POST | `/api/ues`                               | Lister / créer une UE                           |
| GET/PUT/DELETE | `/api/ues/<id>`                     | Détail / modifier / supprimer                   |
| GET | `/api/ues/<id>/groupes`                      | Nombre de groupes calculés (CM/TD/TP/TPE)       |
| GET | `/api/ues/<id>/charge`                       | Charge horaire détaillée de l'UE                |
| GET | `/api/ues/<id>/disponibilite?type=TD`        | Groupes libres/occupés (ou heures restantes CM) |
| GET | `/api/ues/<id>/etat`                         | Vue complète (groupes + charge + disponibilité) |
| GET | `/api/ues/semestres`                         | Liste des semestres existants                   |
| GET/POST | `/api/enseignants`                       | Lister / créer un enseignant                    |
| GET/PUT/DELETE | `/api/enseignants/<id>`            | Détail / modifier / supprimer                   |
| GET | `/api/enseignants/<id>/charge`               | Détail intervention par intervention            |
| GET/POST | `/api/interventions`                     | Lister / créer une affectation (validée)        |
| DELETE | `/api/interventions/<id>`                  | Retirer une affectation                         |
| GET | `/api/dashboard`                             | Détail par UE de tous les enseignants           |
| GET | `/api/recapitulatif?semestre=S3`             | Charge totale par enseignant (période au choix) |
| POST | `/api/simulation`                           | Simuler un changement d'effectif                |
| GET | `/api/export/enseignants`                    | Télécharger le tableau Excel récapitulatif      |

## Déploiement en production

L'application est prête pour un déploiement web (Render, Railway, PythonAnywhere...) :
- `Procfile` : `web: gunicorn run:app`
- `requirements.txt` inclut `gunicorn` et `psycopg2-binary` (pilote PostgreSQL)
- `app/config.py` lit `SECRET_KEY` et `DATABASE_URL` depuis les variables
  d'environnement ; en leur absence, l'application retombe sur une base
  SQLite locale (pratique pour développer sans rien configurer)

### Base de données en production

En local, aucune configuration n'est nécessaire : une base SQLite est créée
automatiquement (`teaching_load.db`).

En production, il est recommandé d'utiliser une vraie base PostgreSQL
(persistante), par exemple gratuitement sur [Neon](https://neon.tech) :
1. Créer un projet Neon et copier la chaîne de connexion fournie
   (`postgresql://...`).
2. La définir comme variable d'environnement `DATABASE_URL` chez
   l'hébergeur (Render, Railway...).
3. Les tables sont créées automatiquement au démarrage de l'application
   (`db.create_all()`).

**Important** : la commande `flask seed` réinitialise entièrement la base
(`db.drop_all()` puis réinsertion de l'exemple de démonstration). Ne
l'exécutez qu'une seule fois, juste après avoir connecté une base neuve —
ne la relancez jamais une fois que de vraies données ont été saisies, sous
peine de tout effacer. Si vous voulez que les utilisateurs partent d'une
base vide (sans l'exemple « Biochimie métabolique »), ne lancez pas cette
commande du tout : les tables vides sont créées automatiquement au premier
démarrage.
