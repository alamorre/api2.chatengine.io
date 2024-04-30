import pytz
from datetime import datetime, timedelta

from rest_framework.utils import json
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from projects.models import User, Project, Person, Collaborator, Promo
from projects.views import Projects

from chats.models import Chat

USER = 'adam@gmail.com'
PASSWORD = 'potato_123'

PROJECT = "Chat Engine 1"

USER_2 = 'adam@gmail.ca'
PROMO_CODE = 'adam'


class GetProjectsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email=USER, password=PASSWORD)
        self.project = Project.objects.create(owner=self.user, title=PROJECT)

    def test_get_projects(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.get('/projects/')
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data[0]['owner'], USER)
        self.assertEqual(response.data[0]['title'], PROJECT)
        self.assertEqual(response.data[0]['count_people'], 0)
        self.assertEqual(response.data[0]['count_chats'], 0)

    def test_get_project_as_member(self):
        temp_user = User.objects.create_user(email=USER_2, password=PASSWORD)
        Collaborator.objects.create(user=temp_user, project=self.project)

        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.get('/projects/')
        force_authenticate(request, user=temp_user)
        response = view(request)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data[0]['owner'], USER)
        self.assertEqual(response.data[0]['title'], PROJECT)
        self.assertEqual(response.data[0]['count_people'], 0)
        self.assertEqual(response.data[0]['count_chats'], 0)

    def test_get_projects_chats_and_people(self):
        person = Person.objects.create(project=self.project, username='...', secret='...')
        Chat.objects.create(project=self.project, admin=person)

        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.get('/projects/')
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['count_people'], 1)
        self.assertEqual(response.data[0]['count_chats'], 1)

    def test_get_projects_needs_auth(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.get('/projects/')
        response = view(request)

        self.assertEqual(response.status_code, 403)


class PostProjectsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email=USER, password=PASSWORD)
        self.promo = Promo.objects.create(code=PROMO_CODE)

    def test_post_project(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({"title": PROJECT}),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        response = view(request)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Project.objects.all()), 1)
        # self.assertEqual(response.data['project']['owner'], USER)
        # self.assertEqual(response.data['project']['title'], PROJECT)
        # self.assertEqual(response.data['project']['is_active'], False)
        # self.assertEqual(type(response.data['stripe_link']), str)    
        # self.assertEqual(response.data['is_active'], False) 
        self.assertEqual(response.data['owner'], USER)
        self.assertEqual(response.data['title'], PROJECT)
        self.assertEqual(response.data['is_active'], True)

    def test_post_project_owner_collaborator_sync(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({"title": PROJECT}),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Project.objects.all()), 1)
        self.assertEqual(len(Collaborator.objects.all()), 1)

        project = Project.objects.first()
        self.assertEqual(project.is_active, True)

        in_ten_days = (datetime.now().replace(tzinfo=pytz.UTC) + timedelta(days=10)).date()
        self.assertEqual(project.expires_date.day, in_ten_days.day)
        self.assertEqual(project.expires_date.month, in_ten_days.month)
        self.assertEqual(project.expires_date.year, in_ten_days.year)

        collaborator = Collaborator.objects.first()
        self.assertEqual(collaborator.project, project)
        self.assertEqual(collaborator.user, self.user)
        self.assertEqual(collaborator.role, 'admin')

        self.assertEqual(len(Project.objects.all()), 1)
        self.assertEqual(len(Collaborator.objects.all()), 1)

        project.delete()
        self.assertEqual(len(Project.objects.all()), 0)
        self.assertEqual(len(Collaborator.objects.all()), 0)
    
    def test_promo_code(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({"title": PROJECT, "promo_code": PROMO_CODE}),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 201)

        project = Project.objects.first()
        self.assertEqual(project.expires_date, None)
        self.assertEqual(project.promo_code, PROMO_CODE)

    def test_bad_promo_code(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({"title": PROJECT, "promo_code": '.'}),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 201)

        project = Project.objects.first()
        in_ten_days = (datetime.now().replace(tzinfo=pytz.UTC) + timedelta(days=10)).date()
        self.assertEqual(project.expires_date.day, in_ten_days.day)
        self.assertEqual(project.expires_date.month, in_ten_days.month)
        self.assertEqual(project.expires_date.year, in_ten_days.year)

    def test_post_project_needs_auth(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({"title": PROJECT}),
            content_type='application/json'
        )
        response = view(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(Project.objects.all()), 0)

    def test_post_project_needs_title(self):
        factory = APIRequestFactory()
        view = Projects.as_view()
        request = factory.post(
            '/projects/',
            json.dumps({}),
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Project.objects.all()), 0)
