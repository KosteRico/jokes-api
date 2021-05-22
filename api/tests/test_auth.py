from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.models import User
from api.views.auth import get_or_create_token


class TestAuthentication(APITestCase):
    user_data = {'username': 'john', 'password': '1234'}

    def setUp(self) -> None:
        user = User(username=self.user_data['username'])
        user.set_password(self.user_data['password'])
        user.save()

        token = get_or_create_token(user)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def test_login(self):
        response = self.client.post('/api/login/', self.user_data, format='json')
        token = response.data.get('token')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(token)
        self.assertTrue(Token.objects.filter(key=token).exists())

    def test_register(self):
        user2_data = {'username': 'jackson', 'password': '1234qwerty'}

        response = self.client.post('/api/register/', user2_data, format='json')

        token = response.data.get('token')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(token)
        self.assertTrue(Token.objects.filter(key=token).exists())

    def test_logout(self):
        tokens_count = Token.objects.count()

        response = self.client.post('/api/logout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Token.objects.count(), tokens_count - 1)
