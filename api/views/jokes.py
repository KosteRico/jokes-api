import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Joke
from api.serializers import JokeSerializer
from jokes_api.settings import JOKES_ENDPOINT


class JokesView(APIView):

    def get(self, request: Request):
        jokes = Joke.objects.filter(user=request.user)

        serializer = JokeSerializer(jokes, many=True)

        return Response(serializer.data)

    def post(self, request: Request):
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OneJokeView(APIView):
    def _get_not_found_exception(self, id: int):
        return NotFound(f'Joke with id={id} not found')

    def _get_joke(self, request: Request, id: int):
        try:
            joke = Joke.objects.get(id=id)
        except ObjectDoesNotExist:
            raise self._get_not_found_exception(id)

        if joke.user != request.user:
            raise PermissionDenied(f'Joke with id={id} not allowed')

        return joke

    def patch(self, request: Request, id: int):
        joke = self._get_joke(request, id)

        try:
            new_text = request.data['text']
        except KeyError:
            raise ValidationError("text field isn't specified")

        joke.text = new_text
        joke.save()

        return Response(status=status.HTTP_200_OK)

    def get(self, request: Request, id: int):
        joke = self._get_joke(request, id)
        serializer = JokeSerializer(joke)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, id: int):
        joke = self._get_joke(request, id)

        number_deleted = joke.delete()[0]

        if number_deleted == 0:
            raise self._get_not_found_exception(id)

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def generate_joke(request: Request):
    r = requests.get(JOKES_ENDPOINT)

    if r.status_code != status.HTTP_200_OK:
        return Response({'detail': r.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    joke_text = r.text.strip('"\n')

    joke = Joke(user=request.user, text=joke_text)
    joke.save()

    serializer = JokeSerializer(joke)

    return Response(serializer.data, status=status.HTTP_201_CREATED)
