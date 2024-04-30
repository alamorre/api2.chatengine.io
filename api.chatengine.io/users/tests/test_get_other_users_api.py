from rest_framework.utils import json
from rest_framework.test import APITestCase, RequestsClient

from chats.models import Person, Chat

from projects.models import User, Project

user_email_1 = 'adam@gmail.com'
user_password_1 = 'potato_123'

user_email_2 = 'eve@gmail.com'

project_title_1 = "Chat Engine Project 1"


class GetMyDetailsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email=user_email_1, password=user_password_1)
        self.project = Project.objects.create(owner=self.user, title=project_title_1)
        self.person_1 = Person.objects.create(project=self.project, username=user_email_1, secret=user_password_1)
        self.person_2 = Person.objects.create(project=self.project, username=user_email_2, secret=user_password_1)
        self.client = RequestsClient()

    def test_get_my_person(self):       
        response = self.client.get(
            'http://127.0.0.1:8000/users/search/',
            headers={
                "public-key": str(self.project.public_key),
                "user-name": user_email_1,
                "user-secret": user_password_1
            }
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        # Not User1 email...
        self.assertEqual(data[0]['username'], user_email_2)

    def test_get_my_person_needs_auth(self):
        response = self.client.get(
            'http://127.0.0.1:8000/users/me/',
            headers={
                "public-key": str(self.project.public_key),
                "user-name": user_email_1
            }
        )

        self.assertEqual(response.status_code, 403)