from rest_framework.test import APITestCase
from api.models import User, Project, Issue, Comment


class ApiTest(APITestCase):
    """
    Classe de base pour les tests d'API.
    Contient l'ensemble des données de test, des méthodes de formatage et de gestion des utilisateurs.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create_user(
            username='user_1',
            password='password',
            age=30,
            can_be_contacted=True,
            can_data_be_shared=True,
        )
        cls.user_2 = User.objects.create_user(
            username='user_2',
            password='password',
            age=25,
            can_be_contacted=False,
            can_data_be_shared=True,
        )
        cls.user_3 = User.objects.create_user(
            username='user_3',
            password='password',
            age=20,
            can_be_contacted=False,
            can_data_be_shared=True,
        )
        cls.project_1 = Project.objects.create(
            author=cls.user_1,
            title='Project 1',
            description='BACKEND',
        )
        cls.contributor_1 = cls.project_1.add_contributor(cls.user_2)
        cls.issue_1 = Issue.objects.create(
            author=cls.user_1,
            project=cls.project_1,
            title='Issue 1',
            description='Description of issue 1',
            priority=Issue.LOW,
            type=Issue.BUG,
            status=Issue.TODO,
        )
        cls.comment_1 = Comment.objects.create(
            author=cls.user_1,
            issue=cls.issue_1,
            description='Comment on issue 1',
        )

    def format_datetime(self, value):
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def log_user_in(self, user):
        response = self.client.post('/api/token/', {
            'username': user.username,
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def log_user_out(self):
        self.client.credentials()

    def get_user_summary_data(self, users):
        return [
            {
                'id': user.id,
                'username': user.username,
            } for user in users
        ]

    def get_user_detail_data(self, user):
        return {
            'id': user.id,
            'username': user.username,
            'age': user.age,
            'can_be_contacted': user.can_be_contacted,
            'can_data_be_shared': user.can_data_be_shared,
        }

    def get_project_list_data(self, projects):
        return [
            {
                'id': project.id,
                'title': project.title,
                'author': project.author.id,
                'description': project.description,
                'created_time': self.format_datetime(project.created_time),
            } for project in projects
        ]

    def get_project_detail_data(self, project):
        return {
            'id': project.id,
            'title': project.title,
            'author': project.author.id,
            'description': project.description,
            'created_time': self.format_datetime(project.created_time),
            'contributors': self.get_user_summary_data(User.objects.filter(contributions__project=project)),
            'issues': self.get_issue_list_data(project.issues.all()),
        }

    def get_issue_list_data(self, issues):
        return [
            {
                'id': issue.id,
                'title': issue.title,
                'description': issue.description,
                'author': issue.author.id,
                'project': issue.project.id,
                'priority': issue.priority,
                'type': issue.type,
                'status': issue.status,
                'created_time': self.format_datetime(issue.created_time),
            } for issue in issues
        ]

    def get_issue_detail_data(self, issue):
        return {
            'id': issue.id,
            'title': issue.title,
            'description': issue.description,
            'author': issue.author.id,
            'project': issue.project.id,
            'priority': issue.priority,
            'type': issue.type,
            'status': issue.status,
            'created_time': self.format_datetime(issue.created_time),
            'comments': self.get_comment_list_data(issue.comments.all()),
        }

    def get_comment_list_data(self, comments):
        return [
            {
                'author': comment.author.id,
                'issue': comment.issue.id,
                'description': comment.description,
                'uuid': str(comment.uuid),
                'created_time': self.format_datetime(comment.created_time),
            } for comment in comments
        ]

    def get_comment_detail_data(self, comment):
        return {
            'author': comment.author.id,
            'issue': comment.issue.id,
            'description': comment.description,
            'uuid': str(comment.uuid),
            'created_time': self.format_datetime(comment.created_time),
        }


class UserTests(ApiTest):
    """
    Tests pour les endpoints du modèle User.
    Pour chaque User, on vérifie les opérations : list, create, detail, update, partial_update et delete.
    Et pour chaque operation, on teste les permissions :
    - non authentifié (unauth)
    - authentifié (auth) en tant qu'utilisateur différent (other)
    - authentifié (auth) en tant que soi-même (self).
    """
    def setUp(self):
        pass

    def test_list_unauth(self):
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, 401)

    def test_list_auth(self):
        self.log_user_in(self.user_1)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_summary_data(User.objects.all())
        self.assertEqual(response.json()['results'], expected)

    def test_create_unauth(self):
        user_count = User.objects.count()
        response = self.client.post('/api/user/', data={
            'username': 'new_user',
            'password': 'new_password',
            'age': 28,
            'can_be_contacted': True,
            'can_data_be_shared': False,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), user_count + 1)

    def test_create_unauth_age_under_15(self):
        user_count = User.objects.count()
        response = self.client.post('/api/user/', data={
            'username': 'new_user',
            'password': 'new_password',
            'age': 14,
            'can_be_contacted': True,
            'can_data_be_shared': False,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), user_count)

    def test_create_auth(self):
        self.log_user_in(self.user_1)
        user_count = User.objects.count()
        response = self.client.post('/api/user/', data={
            'username': 'new_user',
            'password': 'new_password',
            'age': 28,
            'can_be_contacted': True,
            'can_data_be_shared': False,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), user_count)

    def test_detail_unauth(self):
        response = self.client.get(f'/api/user/{self.user_1.id}/')
        self.assertEqual(response.status_code, 401)

    def test_detail_auth_other(self):
        self.log_user_in(self.user_1)
        response = self.client.get(f'/api/user/{self.user_2.id}/')
        self.assertEqual(response.status_code, 403)

    def test_detail_auth_self(self):
        self.log_user_in(self.user_1)
        response = self.client.get(f'/api/user/{self.user_1.id}/')
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_detail_data(self.user_1)
        self.assertEqual(response.json(), expected)

    def test_update_unauth(self):
        response = self.client.put(f'/api/user/{self.user_1.id}/', data={
            'username': 'updated_user'
        })
        self.assertEqual(response.status_code, 401)

    def test_update_auth_other(self):
        self.log_user_in(self.user_1)
        response = self.client.put(f'/api/user/{self.user_2.id}/', data={
            'username': 'updated_user',
            'age': 26,
            'can_be_contacted': False,
            'can_data_be_shared': False,
        })
        self.assertEqual(response.status_code, 403)

    def test_update_auth_self(self):
        self.log_user_in(self.user_1)
        response = self.client.put(f'/api/user/{self.user_1.id}/', data={
            'username': 'updated_user',
            'age': 26,
            'can_be_contacted': False,
            'can_data_be_shared': False,
        })
        self.assertEqual(response.status_code, 200)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.username, 'updated_user')
        self.assertEqual(self.user_1.age, 26)
        self.assertFalse(self.user_1.can_be_contacted)
        self.assertFalse(self.user_1.can_data_be_shared)

    def test_partial_update_unauth(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(f'/api/user/{self.user_2.id}/', data={
            'username': 'updated_user',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_auth_other(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(f'/api/user/{self.user_2.id}/', data={
            'username': 'updated_user',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_auth_self(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(f'/api/user/{self.user_1.id}/', data={
            'username': 'updated_user',
        })
        self.assertEqual(response.status_code, 200)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.username, 'updated_user')

    def test_delete_unauth(self):
        response = self.client.delete(f'/api/user/{self.user_1.id}/')
        self.assertEqual(response.status_code, 401)

    def test_delete_auth_other(self):
        self.log_user_in(self.user_1)
        response = self.client.delete(f'/api/user/{self.user_2.id}/')
        self.assertEqual(response.status_code, 403)

    def test_delete_auth_self(self):
        self.log_user_in(self.user_1)
        user_count = User.objects.count()
        response = self.client.delete(f'/api/user/{self.user_1.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.count(), user_count - 1)


class ProjectTests(ApiTest):
    """
    Tests pour les endpoints du modèle Project.
    Pour chaque Project, on vérifie les opérations : list, create, detail, update, partial_update et delete.
    Et pour chaque operation, on teste les permissions :
    - non authentifié (unauth)
    - authentifié (auth) en tant qu'auteur (author)
    - authentifié (auth) en tant que contributeur (contributor)
    - authentifié (auth) en tant qu'autre utilisateur (other)
    """
    def setUp(self):
        self.url = '/api/project/'
        self.url_detail = f'{self.url}{self.project_1.id}/'

    def test_list_unauth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_list_auth(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_list_data(Project.objects.all())
        self.assertEqual(response.json()['results'], expected)

    def test_create_unauth(self):
        response = self.client.post(self.url, data={
            'title': 'New Project',
            'description': 'BACKEND',
        })
        self.assertEqual(response.status_code, 401)

    def test_create_auth(self):
        self.log_user_in(self.user_1)
        project_count = Project.objects.count()
        response = self.client.post(self.url, data={
            'title': 'New Project',
            'description': 'BACKEND',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.count(), project_count + 1)

    def test_detail_unauth(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_detail_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_detail_data(self.project_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_detail_data(self.project_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 403)

    def test_update_unauth(self):
        response = self.client.put(self.url_detail, data={
            'title': 'Updated Project',
            'description': 'FRONTEND',
        })
        self.assertEqual(response.status_code, 401)

    def test_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.put(self.url_detail, data={
            'title': 'Updated Project',
            'description': 'FRONTEND',
        })
        self.assertEqual(response.status_code, 200)
        self.project_1.refresh_from_db()
        self.assertEqual(self.project_1.title, 'Updated Project')
        self.assertEqual(self.project_1.description, 'FRONTEND')

    def test_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.put(self.url_detail, data={
            'title': 'Updated Project',
            'description': 'FRONTEND',
        })
        self.assertEqual(response.status_code, 403)

    def test_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.put(self.url_detail, data={
            'title': 'Updated Project',
            'description': 'FRONTEND',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_unauth(self):
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Project',
        })
        self.assertEqual(response.status_code, 401)

    def test_partial_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Project',
        })
        self.assertEqual(response.status_code, 200)
        self.project_1.refresh_from_db()
        self.assertEqual(self.project_1.title, 'Partially Updated Project')

    def test_partial_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Project',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Project',
        })
        self.assertEqual(response.status_code, 403)

    def test_delete_unauth(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_delete_auth_author(self):
        self.log_user_in(self.user_1)
        project_count = Project.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Project.objects.count(), project_count - 1)

    def test_delete_auth_contributor(self):
        self.log_user_in(self.user_2)
        project_count = Project.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), project_count)

    def test_delete_auth_other(self):
        self.log_user_in(self.user_3)
        project_count = Project.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), project_count)

    def test_add_contributor_unauth(self):
        response = self.client.post(f'{self.url_detail}add_contributor/', data={
            'user': self.user_3.id,
        })
        self.assertEqual(response.status_code, 401)

    def test_add_contributor_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.post(f'{self.url_detail}add_contributor/', data={
            'user': self.user_3.id,
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.project_1.contributors.filter(user=self.user_3).exists())

    def test_add_contributor_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.post(f'{self.url_detail}add_contributor/', data={
            'user': self.user_3.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_add_contributor_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.post(f'{self.url_detail}add_contributor/', data={
            'user': self.user_3.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_remove_contributor_unauth(self):
        response = self.client.post(f'{self.url_detail}remove_contributor/', data={
            'user': self.user_2.id,
        })
        self.assertEqual(response.status_code, 401)

    def test_remove_contributor_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.post(f'{self.url_detail}remove_contributor/', data={
            'user': self.user_2.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.project_1.contributors.filter(user=self.user_2).exists())

    def test_remove_contributor_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.post(f'{self.url_detail}remove_contributor/', data={
            'user': self.user_2.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_remove_contributor_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.post(f'{self.url_detail}remove_contributor/', data={
            'user': self.user_2.id,
        })
        self.assertEqual(response.status_code, 403)


class IssueTests(ApiTest):
    """
    Tests pour les endpoints du modèle Issue.
    Pour chaque Issue, on vérifie les opérations : list, create, detail, update, partial_update et delete.
    Et pour chaque operation, on teste les permissions :
    - non authentifié (unauth)
    - authentifié (auth) en tant qu'auteur du projet (project_author)
    - authentifié (auth) en tant qu'auteur de l'issue (author)
    - authentifié (auth) en tant que contributeur du projet (contributor)
    - authentifié (auth) en tant qu'autre utilisateur (other)
    """
    def setUp(self):
        self.url = f'/api/project/{self.project_1.id}/issue/'
        self.url_detail = f'{self.url}{self.issue_1.id}/'

    def test_list_unauth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_list_auth_project_author(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issue_list_data(self.project_1.issues.all())
        self.assertEqual(response.json()['results'], expected)

    def test_list_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issue_list_data(self.project_1.issues.all())
        self.assertEqual(response.json()['results'], expected)

    def test_list_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_unauth(self):
        response = self.client.post(self.url, data={
            'title': 'New Issue',
            'description': 'Description of new issue',
            'priority': Issue.LOW,
            'type': Issue.BUG,
            'status': Issue.TODO,
        })
        self.assertEqual(response.status_code, 401)

    def test_create_auth_project_author_for_contributor(self):
        self.log_user_in(self.user_1)
        issue_count = Issue.objects.count()
        response = self.client.post(self.url, data={
            'author': self.user_2.id,
            'title': 'New Issue',
            'description': 'Description of new issue',
            'priority': Issue.LOW,
            'type': Issue.BUG,
            'status': Issue.TODO,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Issue.objects.count(), issue_count + 1)

    def test_create_auth_project_author_for_non_contributor(self):
        self.log_user_in(self.user_1)
        issue_count = Issue.objects.count()
        response = self.client.post(self.url, data={
            'author': self.user_3.id,
            'title': 'New Issue',
            'description': 'Description of new issue',
            'priority': Issue.LOW,
            'type': Issue.BUG,
            'status': Issue.TODO,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Issue.objects.count(), issue_count)

    def test_create_auth_contributor(self):
        self.log_user_in(self.user_2)
        issue_count = Issue.objects.count()
        response = self.client.post(self.url, data={
            'author': self.user_2.id,
            'title': 'New Issue',
            'description': 'Description of new issue',
            'priority': Issue.LOW,
            'type': Issue.BUG,
            'status': Issue.TODO,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Issue.objects.count(), issue_count + 1)

    def test_create_auth_other(self):
        self.log_user_in(self.user_3)
        issue_count = Issue.objects.count()
        response = self.client.post(self.url, data={
            'author': self.user_2.id,
            'title': 'New Issue',
            'description': 'Description of new issue',
            'priority': Issue.LOW,
            'type': Issue.BUG,
            'status': Issue.TODO,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Issue.objects.count(), issue_count)

    def test_detail_unauth(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_detail_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issue_detail_data(self.issue_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issue_detail_data(self.issue_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 403)

    def test_update_unauth(self):
        response = self.client.put(self.url_detail, data={
            'author': self.user_2.id,
            'title': 'Updated Issue',
            'description': 'Updated description',
            'priority': Issue.MEDIUM,
            'type': Issue.FEATURE,
            'status': Issue.IN_PROGRESS,
        })
        self.assertEqual(response.status_code, 401)

    def test_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.put(self.url_detail, data={
            'author': self.user_2.id,
            'title': 'Updated Issue',
            'description': 'Updated description',
            'priority': Issue.MEDIUM,
            'type': Issue.FEATURE,
            'status': Issue.IN_PROGRESS,
        })
        self.assertEqual(response.status_code, 200)
        self.issue_1.refresh_from_db()
        self.assertEqual(self.issue_1.author, self.user_2)
        self.assertEqual(self.issue_1.title, 'Updated Issue')
        self.assertEqual(self.issue_1.description, 'Updated description')
        self.assertEqual(self.issue_1.priority, Issue.MEDIUM)
        self.assertEqual(self.issue_1.type, Issue.FEATURE)
        self.assertEqual(self.issue_1.status, Issue.IN_PROGRESS)

    def test_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.put(self.url_detail, data={
            'author': self.user_2.id,
            'title': 'Updated Issue',
            'description': 'Updated description',
            'priority': 'MEDIUM',
            'type': 'FEATURE',
            'status': 'IN_PROGRESS',
        })
        self.assertEqual(response.status_code, 403)

    def test_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.put(self.url_detail, data={
            'author': self.user_2.id,
            'title': 'Updated Issue',
            'description': 'Updated description',
            'priority': Issue.MEDIUM,
            'type': Issue.FEATURE,
            'status': Issue.IN_PROGRESS,
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_unauth(self):
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Issue',
        })
        self.assertEqual(response.status_code, 401)

    def test_partial_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Issue',
        })
        self.assertEqual(response.status_code, 200)
        self.issue_1.refresh_from_db()
        self.assertEqual(self.issue_1.title, 'Partially Updated Issue')

    def test_partial_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Issue',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.patch(self.url_detail, data={
            'title': 'Partially Updated Issue',
        })
        self.assertEqual(response.status_code, 403)

    def test_delete_unauth(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_delete_auth_author(self):
        self.log_user_in(self.user_1)
        issue_count = Issue.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Issue.objects.count(), issue_count - 1)

    def test_delete_auth_contributor(self):
        self.log_user_in(self.user_2)
        issue_count = Issue.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Issue.objects.count(), issue_count)

    def test_delete_auth_other(self):
        self.log_user_in(self.user_3)
        issue_count = Issue.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Issue.objects.count(), issue_count)


class CommentTests(ApiTest):
    """
    Tests pour les endpoints du modèle Comment.
    Pour chaque Comment, on vérifie les opérations : list, create, detail, update, partial_update et delete.
    Et pour chaque operation, on teste les permissions :
    - non authentifié (unauth)
    - authentifié (auth) en tant qu'auteur du projet (project_author)
    - authentifié (auth) en tant qu'auteur du comment (author)
    - authentifié (auth) en tant que contributeur du projet (contributor)
    - authentifié (auth) en tant qu'autre utilisateur (other)
    """
    def setUp(self):
        self.url = f'/api/project/{self.project_1.id}/issue/{self.issue_1.id}/comment/'
        self.url_detail = f'{self.url}{self.comment_1.uuid}/'

    def test_list_unauth(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_list_auth_project_author(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comment_list_data(self.issue_1.comments.all())
        self.assertEqual(response.json()['results'], expected)

    def test_list_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comment_list_data(self.issue_1.comments.all())
        self.assertEqual(response.json()['results'], expected)

    def test_list_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_create_unauth(self):
        response = self.client.post(self.url, data={
            'description': 'New comment on issue',
        })
        self.assertEqual(response.status_code, 401)

    def test_create_auth_project_author(self):
        self.log_user_in(self.user_1)
        comment_count = Comment.objects.count()
        response = self.client.post(self.url, data={
            'description': 'New comment on issue',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_auth_contributor(self):
        self.log_user_in(self.user_2)
        comment_count = Comment.objects.count()
        response = self.client.post(self.url, data={
            'description': 'New comment on issue',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_create_auth_other(self):
        self.log_user_in(self.user_3)
        comment_count = Comment.objects.count()
        response = self.client.post(self.url, data={
            'description': 'New comment on issue',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_detail_unauth(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_detail_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comment_detail_data(self.comment_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comment_detail_data(self.comment_1)
        self.assertEqual(response.json(), expected)

    def test_detail_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 403)

    def test_update_unauth(self):
        response = self.client.put(self.url_detail, data={
            'description': 'Updated comment',
        })
        self.assertEqual(response.status_code, 401)

    def test_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.put(self.url_detail, data={
            'description': 'Updated comment',
        })
        self.assertEqual(response.status_code, 200)
        self.comment_1.refresh_from_db()
        self.assertEqual(self.comment_1.description, 'Updated comment')

    def test_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.put(self.url_detail, data={
            'description': 'Updated comment',
        })
        self.assertEqual(response.status_code, 403)

    def test_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.put(self.url_detail, data={
            'description': 'Updated comment',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_unauth(self):
        response = self.client.patch(self.url_detail, data={
            'description': 'Partially updated comment',
        })
        self.assertEqual(response.status_code, 401)

    def test_partial_update_auth_author(self):
        self.log_user_in(self.user_1)
        response = self.client.patch(self.url_detail, data={
            'description': 'Partially updated comment',
        })
        self.assertEqual(response.status_code, 200)
        self.comment_1.refresh_from_db()
        self.assertEqual(self.comment_1.description, 'Partially updated comment')

    def test_partial_update_auth_contributor(self):
        self.log_user_in(self.user_2)
        response = self.client.patch(self.url_detail, data={
            'description': 'Partially updated comment',
        })
        self.assertEqual(response.status_code, 403)

    def test_partial_update_auth_other(self):
        self.log_user_in(self.user_3)
        response = self.client.patch(self.url_detail, data={
            'description': 'Partially updated comment',
        })
        self.assertEqual(response.status_code, 403)

    def test_delete_unauth(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 401)

    def test_delete_auth_author(self):
        self.log_user_in(self.user_1)
        comment_count = Comment.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), comment_count - 1)

    def test_delete_auth_contributor(self):
        self.log_user_in(self.user_2)
        comment_count = Comment.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_delete_auth_other(self):
        self.log_user_in(self.user_3)
        comment_count = Comment.objects.count()
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), comment_count)
