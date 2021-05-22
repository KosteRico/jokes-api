from random import randint

from django.db.models import Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api.models import Joke, User
from api.serializers import JokeSerializer


class TestJokeBase(APITestCase):
    """
    Class for user previous users registration and database filling
    """

    def _set_token(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def _register_user(self, data) -> str:
        response = self.client.post('/api/register/', data, format='json')
        return response.data['token']

    def login_random_user(self) -> User:
        user_index = randint(0, len(self.users) - 1)
        self._set_token(self.tokens[user_index])
        return self.users[user_index]

    def setUp(self) -> None:
        self.tokens = []
        self.users = []

        self.tokens.append(self._register_user({'username': 'john', 'password': '1234'}))
        self.tokens.append(self._register_user({'username': 'jack', 'password': '12rwe34'}))

        self.users.append(Token.objects.get(key=self.tokens[0]).user)
        self.users.append(Token.objects.get(key=self.tokens[1]).user)

        Joke.objects.create(user=self.users[0], text="Chuck Norris can strangle you with a cordless phone")
        Joke.objects.create(user=self.users[0],
                            text="Chuck Norris doesn’t wear a watch. He decides what time it is")
        Joke.objects.create(user=self.users[1], text="Chuck Norris lost his virginity before his dad did")
        Joke.objects.create(user=self.users[1], text="Chuck Norris can kill your imaginary friends")
        Joke.objects.create(user=self.users[1], text="Chuck Norris makes onions cry")


class TestJokes(TestJokeBase):

    def check_created(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIsNotNone(response.data.get('id'))

        joke_id = response.data['id']

        serializer = JokeSerializer(Joke.objects.get(id=joke_id))

        self.assertEqual(response.data, serializer.data)

    def test_get(self):
        user = self.login_random_user()

        serializer = JokeSerializer(Joke.objects.filter(user=user), many=True)

        response = self.client.get('/api/jokes/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post(self):
        user = self.login_random_user()

        data = {'text': 'hahaha', 'user': user.username}

        response = self.client.post('/api/jokes/', data, format='json')

        self.check_created(response)

    def test_generate(self):
        self.login_random_user()

        response = self.client.post('/api/jokes/generate/', format='json')

        self.check_created(response)


class TestOneJoke(TestJokeBase):

    def _get_allowed_joke_id(self, user: User) -> int:
        return Joke.objects.filter(user=user)[0].id

    def _get_not_allowed_joke_id(self, user: User) -> int:
        return Joke.objects.filter(~Q(user=user))[0].id

    def test_get(self):
        user = self.login_random_user()
        joke_id = self._get_allowed_joke_id(user)

        response = self.client.get(f'/api/jokes/{joke_id}', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = JokeSerializer(Joke.objects.get(id=joke_id))
        self.assertEqual(serializer.data, response.data)

    def test_get_403(self):
        user = self.login_random_user()
        joke_id = self._get_not_allowed_joke_id(user)

        response = self.client.get(f'/api/jokes/{joke_id}', format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch(self):
        user = self.login_random_user()
        joke_id = self._get_allowed_joke_id(user)

        data = {'text': "hahah"}

        response = self.client.patch(f'/api/jokes/{joke_id}', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Joke.objects.get(id=joke_id).text, data['text'])

    def test_delete(self):
        user = self.login_random_user()
        joke_id = self._get_allowed_joke_id(user)

        response = self.client.delete(f'/api/jokes/{joke_id}', format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Joke.objects.filter(id=joke_id).exists())
