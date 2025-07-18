# Projet 10 - Créez une API sécurisée RESTful en utilisant Django REST

## 📝 Description

**SoftDesk Support** est une **API RESTful** développée en **Django REST Framework** pour gérer des problèmes techniques au sein de projets informatiques. L'application permet à des entreprises en B2B de suivre, documenter et résoudre efficacement les bugs et tâches liés à leurs produits via un système de gestion des utilisateurs, projets, problèmes, et commentaires.

L'API respecte les normes de sécurité **OWASP**, les obligations **RGPD**, ainsi que des pratiques de développement **"green code"** pour optimiser les performances serveur.

---

## 🖥️ Fonctionnalités

- 🔐 Authentification via **JWT**
- 👤 Gestion des **utilisateurs** avec consentement RGPD
- 📁 Création et gestion de **projets**
- 👥 Ajout de **contributeurs** par projet
- 🐞 Création et suivi de **problèmes** :
- 💬 **Commentaires** associés aux problèmes
- 🔒 **Permissions** strictes en fonction de de l'utilisateur, de la ressource et du type d'action
- 📅 **Horodatage** automatique des ressources
- 📄 **Pagination** de toutes les ressources listées

---

## 📥 Installation et exécution

### 1️⃣ Cloner le projet

```sh
cd "chemin/vers/dossier/souhaité/"
git clone https://github.com/Matthieu-Chambon/OC_Projet_10
```

### 2️⃣ Installer le projet

```sh
cd OC_Projet_10
poetry install
poetry shell
python manage.py migrate
```

### 3️⃣ Lancer le serveur

```sh
python manage.py runserver
```

### 4️⃣ Accéder à l’application

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 5️⃣ Créer des données fictives

```sh
python populate.py
```

À la fin de l'exécution, le script affiche les identifiants de connexion des faux utilisateurs ainsi que du super utilisateur.

---

## 🔗 Liste des endpoints

| 🧩 Modèle  | Méthode          | URL (pattern)                                              | Description                            | Accès requis           |
| ---------- | ---------------- | ---------------------------------------------------------- | -------------------------------------- | ---------------------- |
| 🔑 Token   | POST             | `/api/token/`                                              | Obtenir un token JWT                   | Public                 |
| 🔑 Token   | POST             | `/api/token/refresh/`                                      | Rafraîchir un token JWT                | Authentifié            |
| 👤 User    | POST             | `/api/user/`                                               | Créer un compte utilisateur            | Public                 |
| 👤 User    | GET              | `/api/user/`                                               | Lister tous les utilisateurs           | Authentifié            |
| 👤 User    | GET              | `/api/user/{id}/`                                          | Voir son propre profil                 | Propriétaire uniquemen |
| 👤 User    | PUT/PATCH/DELETE | `/api/user/{id}/`                                          | Modifier / Supprimer son propre profil | Propriétaire uniquemen |
| 📁 Project | POST             | `/api/project/`                                            | Créer un projet                        | Authentifié            |
| 📁 Project | GET              | `/api/project/`                                            | Lister les projets                     | Authentifié            |
| 📁 Project | GET              | `/api/project/{pk}/`                                       | Voir un projet                         | Auteur ou contributeur |
| 📁 Project | PUT/PATCH/DELETE | `/api/project/{pk}/`                                       | Modifier / Supprimer un projet         | Auteur uniquement      |
| 📁 Project | POST             | `/api/project/{pk}/add_contributor/`                       | Ajouter un contributeur à un projet    | Auteur uniquement      |
| 📁 Project | POST             | `/api/project/{pk}/remove_contributor/`                    | Retirer un contributeur d’un projet    | Auteur uniquement      |
| 🐛 Issue   | GET/POST         | `/api/project/{project_pk}/issue/`                         | Lister ou créer des problèmes          | Contributeur ou auteur |
| 🐛 Issue   | GET              | `/api/project/{project_pk}/issue/{pk}/`                    | Détail d’un problème                   | Contributeur ou auteur |
| 🐛 Issue   | PUT/PATCH/DELETE | `/api/project/{project_pk}/issue/{pk}/`                    | Modifier / Supprimer un problème       | Auteur uniquement      |
| 💬 Comment | GET/POST         | `/api/project/{project_pk}/issue/{issue_pk}/comment/`      | Lister ou créer des commentaires       | Contributeur ou auteur |
| 💬 Comment | GET              | `/api/project/{project_pk}/issue/{issue_pk}/comment/{pk}/` | Voir un commentaire                    | Contributeur ou auteur |
| 💬 Comment | PUT/PATCH/DELETE | `/api/project/{project_pk}/issue/{issue_pk}/comment/{pk}/` | Modifier / Supprimer un commentaire    | Auteur uniquement      |

---

## 🛠️ Technologies utilisées

* 🐍 [Python](https://www.python.org/)
* 🌐 [Django](https://www.djangoproject.com/)
* 🔧 [Django REST Framework](https://www.django-rest-framework.org/)
* 🗃️ [SQLite](https://www.sqlite.org/docs.html)
* 🔐 [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)
* 🎲 [Faker](https://faker.readthedocs.io/en/master/)
* 📦 [Poetry](https://python-poetry.org/)

---

## ✅ Conformité

* ✅ Respect des bonnes pratiques **Django**
* ✅ Respect des normes **PEP8** (via Flake8)
* ✅ Sécurité **OWASP** : Authentification, permissions strictes
* ✅ Conformité **RGPD** : Données personnelles protégées, consentement vérifié
* ✅ Approche **Green code** : Sérialisations optimisées, pagination, requêtes filtrées
* ✅ Mises à jour de sécurité automatisées grâce à **Dependabot**
