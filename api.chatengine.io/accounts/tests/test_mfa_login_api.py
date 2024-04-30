from rest_framework.utils import json
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from accounts.models import User
from accounts.views import MultiFactorLogin

user_email_1 = 'adam@gmail.com'
user_password_1 = 'potato_123'

user_email_2 = 'eve@gmail.com'
user_password_2 = 'guacamole_123'


class LoginTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=user_email_1, password=user_password_1)

    def test_login(self):
        factory = APIRequestFactory()
        view = MultiFactorLogin.as_view()
        request = factory.post(
            '/accounts/mfa/',
            json.dumps({
                "email": user_email_1, 
                "password": user_password_1, 
                "mfa_code": str(self.user.mfa_code)
            }),
            content_type='application/json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['token'], None)
        self.assertEqual(response.data['user']['email'], user_email_1)

    def test_login_bad_email(self):
        factory = APIRequestFactory()
        view = MultiFactorLogin.as_view()
        request = factory.post(
            '/accounts/mfa/',
            json.dumps({
                "email": 'not@email.com', 
                "password": user_password_1, 
                "mfa_code": str(self.user.mfa_code)
            }),
            content_type='application/json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_login_bad_password(self):
        factory = APIRequestFactory()
        view = MultiFactorLogin.as_view()
        request = factory.post(
            '/accounts/mfa/',
            json.dumps({
                "email": user_email_1, 
                "password": 'bad_pw_123!', 
                "mfa_code": str(self.user.mfa_code)
            }),
            content_type='application/json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 404)

    def test_login_bad_mfa_code(self):
        factory = APIRequestFactory()
        view = MultiFactorLogin.as_view()
        request = factory.post(
            '/accounts/mfa/',
            json.dumps({
                "email": user_email_1, 
                "password": user_password_1, 
                "mfa_code": '00000000-0000-0000-0000-000000000000'
            }),
            content_type='application/json'
        )
        response = view(request)
        self.assertEqual(response.status_code, 404)
