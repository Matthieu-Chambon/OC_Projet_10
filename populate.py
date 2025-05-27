import os
import django
import random
import uuid
from faker import Faker
from django.utils.timezone import now

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SoftDesk.settings')
django.setup()

from api.models import User, Contributor, Project, Issue, Comment

fake = Faker('fr_FR')

def run():
    Comment.objects.all().delete()
    Issue.objects.all().delete()
    Project.objects.all().delete()
    Contributor.objects.all().delete()
    User.objects.all().delete()
    
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
            password='user',
            age=random.randint(18, 60),
            can_be_contacted=fake.boolean(),
            can_data_be_shared=fake.boolean(),
        )
        users.append(user)

    project_titles = [
        "Application de gestion",
        "Plateforme collaborative",
        "Outil de planification",
        "Interface utilisateur moderne",
        "API de suivi de bugs",
        "Dashboard analytique",
    ]
    
    projects = []
    for _ in range(3):
        author = random.choice(users)
        project = Project.objects.create(
            author=author,
            title = random.choice(project_titles),
            description=random.choice(['BACKEND', 'FRONTEND', 'IOS', 'ANDROID']),
        )
        projects.append(project)

    issues = []
    for _ in range(10):
        project = random.choice(projects)
        author = random.choice(users)
        issue = Issue.objects.create(
            project=project,
            author=author,
            title=fake.sentence(nb_words=4),
            description=fake.paragraph(nb_sentences=2),
            priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
            type=random.choice(['BUG', 'FEATURE', 'TASK']),
            status=random.choice(['TODO', 'IN_PROGRESS', 'FINISHED']),
        )
        issues.append(issue)

    for _ in range(15):
        issue = random.choice(issues)
        author = random.choice(users)
        Comment.objects.create(
            issue=issue,
            author=author,
            description=fake.text(max_nb_chars=200),
            uuid=uuid.uuid4(),
            created_time=now()
        )

if __name__ == '__main__':
    # > python populate.py
    run()
    print("Données de test insérées !")