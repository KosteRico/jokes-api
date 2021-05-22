from typing import Tuple

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import User


def get_username_password(request) -> Tuple[str, str]:
    p = request.data
    return p.get('username'), p.get('password')


def get_or_create_token(user: User) -> str:
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@api_view(['POST'])
@permission_classes((AllowAny,))
def register_view(request):
    username, password = get_username_password(request)

    user = User(username=username)
    user.set_password(password)
    user.save()

    token = get_or_create_token(user)

    return Response({'token': token}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((AllowAny,))
def login_view(request):
    username, password = get_username_password(request)

    user = authenticate(username=username, password=password)

    if not user:
        raise NotFound(detail="Invalid Credentials")

    token = get_or_create_token(user)

    return Response({'token': token}, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_view(request):
    Token.objects.get(user=request.user).delete()

    return Response(status=status.HTTP_200_OK)
