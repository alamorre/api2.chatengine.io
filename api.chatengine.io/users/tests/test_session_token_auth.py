from rest_framework.utils import json
from rest_framework.test import APITestCase, RequestsClient

from chats.models import Person

from projects.models import User, Project
from users.models import Session

USER = 'adam@gmail.com'
PASSWORD = 'potato_123'

PROJECT = "Chat Engine Project 1"
CHAT = "Chat Engine Chat 1"


class GetPeoplePrivateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email=USER, password=PASSWORD)
        self.project = Project.objects.create(owner=self.user, title=PROJECT)
        self.person = Person.objects.create(project=self.project, username=USER, secret=PASSWORD)
        self.client = RequestsClient()

    def test_session_token_auth(self):
        # Make a session token via api
        response = self.client.get(
            'http://127.0.0.1:8000/users/me/session/',
            headers={
                "public-key": str(self.project.public_key),
                "user-name": USER,
                "user-secret": PASSWORD
            }
        )
        session_token = Session.objects.get(person=self.person).token

        # Use the session token to authenticate
        response = self.client.get(
            'http://127.0.0.1:8000/users/session_auth/{}/'.format(session_token)        
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['token'], session_token)
    
    def test_bad_session_token_auth(self):
        # Use a bad session token 
        session_token = 'st-1234'
        response = self.client.get(
            'http://127.0.0.1:8000/users/session_auth/{}/'.format(session_token)        
        )
        self.assertEqual(response.status_code, 404)