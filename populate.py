import os
import django
import random
from faker import Faker
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SoftDesk.settings')
django.setup()

from api.models import User, Contributor, Project, Issue, Comment  # noqa: E402

fake = Faker('fr_FR')


def run():
    call_command('flush', '--noinput')

    User.objects.create_superuser(
        username='admin',
        password='admin',
        age=24,
        can_be_contacted=True,
        can_data_be_shared=True,
    )

    users = []
    for _ in range(5):
        user = User.objects.create_user(
            username=fake.user_name(),
            password='password',
            age=random.randint(18, 60),
            can_be_contacted=fake.boolean(),
            can_data_be_shared=fake.boolean(),
        )
        users.append(user)

    project_titles = [
        "Application de gestion",
        "Plateforme collaborative",
        "Outil de planification",
    ]

    projects = []
    for i in range(3):
        author = users[i]
        project = Project.objects.create(
            author=author,
            title=project_titles[i],
            description=fake.paragraph(nb_sentences=3),
            type=random.choice(['BACKEND', 'FRONTEND', 'IOS', 'ANDROID']),
        )
        projects.append(project)

    contributors = []
    for project in projects:
        potential_contributors = [user for user in users if user != project.author]
        for _ in range(random.randint(1, 3)):
            contributor = Contributor.objects.create(
                user=random.choice(potential_contributors),
                project=project
            )
            potential_contributors.remove(contributor.user)
            contributors.append(contributor)

    issue_titles = [
        "Problème de performance",
        "Amélioration de l'interface utilisateur",
        "Correction de bug",
        "Ajout de fonctionnalité",
        "Mise à jour de la documentation",
    ]

    issues = []
    for project in projects:
        for i in range(random.randint(3, 5)):
            author = random.choice(project.contributors.all()).user
            issue = Issue.objects.create(
                project=project,
                author=author,
                title=issue_titles[i],
                description=fake.paragraph(nb_sentences=2),
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                type=random.choice(['BUG', 'FEATURE', 'TASK']),
                status=random.choice(['TODO', 'IN_PROGRESS', 'FINISHED']),
            )
        issues.append(issue)

    for issue in issues:
        for _ in range(random.randint(3, 10)):
            author = random.choice(issue.project.contributors.all()).user
            Comment.objects.create(
                issue=issue,
                author=author,
                description=fake.text(max_nb_chars=200),
            )


if __name__ == '__main__':
    # > python populate.py
    print("Insertion des données de test dans la base de données...")
    run()
    print("Données de test insérées !\n")
    print("Liste des faux utilisateurs créés :")
    print("ID : 1, username : 'admin', password : 'admin'")
    for user in User.objects.filter(is_superuser=False):
        print(f"ID : {user.id}, username : '{user.username}', password : 'password'")
