from rest_framework.utils import json
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from accounts.models import User
from accounts.views import CustomObtainAuthToken

user_email_1 = 'adam@gmail.com'
user_password_1 = 'potato_123'

user_email_2 = 'eve@gmail.com'
user_password_2 = 'guacamole_123'


class LoginTestCase(APITestCase):
    def setUp(self):
        User.objects.create_user(email=user_email_1, password=user_password_1)

    def test_login(self):
        factory = APIRequestFactory()
        view = CustomObtainAuthToken.as_view()

        request = factory.post(
            '/accounts/login/',
            json.dumps({"email": user_email_1, "password": user_password_1}),
            content_type='application/json'
        )
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['token'], None)
        self.assertEqual(response.data['user']['email'], user_email_1)
        # self.assertEqual(response.data, "MFA Code has been sent.")

    def test_login_bad_email(self):
        factory = APIRequestFactory()
        view = CustomObtainAuthToken.as_view()

        request = factory.post(
            '/accounts/login/',
            json.dumps({"email": user_email_2, "password": user_password_1}),
            content_type='application/json'
        )
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], "Unable to log in with provided credentials.")

    def test_login_bad_password(self):
        factory = APIRequestFactory()
        view = CustomObtainAuthToken.as_view()

        request = factory.post(
            '/accounts/login/',
            json.dumps({"email": user_email_1, "password": user_password_2}),
            content_type='application/json'
        )
        response = view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], "Unable to log in with provided credentials.")
