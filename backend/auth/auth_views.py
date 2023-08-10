import datetime
from dataclasses import dataclass, asdict

import requests
from allauth import utils
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

CLIENT_ID = '93483542407-ckrg8q5q527dmcd62ptg0am5j9jhvesb.apps.googleusercontent.com'


class NewPasswordViewSet(viewsets.ViewSet):
    def create(self, request):
        return Response(None, status.HTTP_501_NOT_IMPLEMENTED)


class UniqueUserNameCheckerViewSet(viewsets.ViewSet):
    def create(self, request):
        if not 'username' in request.data:
            return Response('invalid input', status.HTTP_403_FORBIDDEN)
        if User.objects.filter(username=request.data['username']).exists():
            return Response(False)
        return Response(True)


class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        if not 'username' in request.data or not 'password' in request.data or not 'email' in request.data \
                or not 'first_name' in request.data or not 'last_name' in request.data:
            return Response('invalid input', status.HTTP_403_FORBIDDEN)
        if len(request.data['username']) < 5:
            return Response('min username length is 5 characters', status.HTTP_403_FORBIDDEN)
        if len(request.data['password']) < 5:
            return Response('min password length is 5 characters', status.HTTP_403_FORBIDDEN)
        if User.objects.filter(username=request.data['username']).exists():
            return Response('username is already taken', status.HTTP_403_FORBIDDEN)
        user = User.objects.create_user(
            username=request.data['username'],
            email=request.data['email'],
            password=request.data['password'],
            last_login=datetime.datetime.now(),
            last_name=request.data['last_name'],
            first_name=request.data['first_name'],
        )
        userdata = Userdata(username=request.data['username'], email=request.data['email'],
                            name=f"{request.data['last_name']} {request.data['first_name']}"
                            )
        token, created = Token.objects.get_or_create(user_id=user.id)
        userdata.token = token.key
        # if userdata.name.strip() == "":
        return JsonResponse(userdata.dict())

    def list(self, request, *args, **kw):
        return Response(request.data)


class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        if not 'username' in request.data or not 'password' in request.data:
            return Response(None, status.HTTP_403_FORBIDDEN)
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if not user:
            return Response('bad credentials', status.HTTP_401_UNAUTHORIZED)
        userdata = Userdata(username=user.username)
        social_account = SocialAccount.objects.filter(uid=user.id).values('user_id')
        if len(social_account) < 1:
            userdata.name = _getNameByUser(user)
            userdata.email = _getEmailByUser(user)
            # todo: установить в рабочей базе стандартную почту для юзеров с пустой почтой
        else:
            userdata.name = social_account[0]["extra_data"]["name"]
            userdata.picture = social_account[0]["extra_data"]["picture"]
            userdata.email = social_account[0]["extra_data"]["email"]
        token, created = Token.objects.get_or_create(user_id=user.id)
        userdata.token = token.key
        return Response(userdata.dict())

    def list(self, request, *args, **kw):
        if not 'HTTP_AUTHORIZATION' in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not 'Token ' in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user
        social_account = SocialAccount.objects.filter(user_id=user.id).values('extra_data')
        userdata = Userdata(username=user.username)
        if len(social_account) > 0:
            userdata.name = social_account[0]["extra_data"]["name"]
            userdata.picture = social_account[0]["extra_data"]["picture"]
            userdata.email = social_account[0]["extra_data"]["email"]
        else:
            userdata.name = _getNameByUser(user)
            userdata.email = _getEmailByUser(user)
        response = JsonResponse(userdata.dict())
        return response


class LogoutEverywhereViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if not 'HTTP_AUTHORIZATION' in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not 'Token ' in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        data = Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).delete()
        response = Response(data)
        return response


class LoginGoogleViewSet(viewsets.ViewSet):
    def create(self, request):
        return JsonResponse(_createOrGetUserDataByGoogleUserInfo(
            requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                'Authorization': f'{request.data["token_type"]} {request.data["access_token"]}'}).json()).dict())


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response('4xx test', status.HTTP_401_UNAUTHORIZED)


def _getEmailByUser(user):
    return user.email if len(user.email.strip()) > 0 else f"{user.username}@mailto.plus"


def _getNameByUser(user):
    return f"{user.first_name} {user.last_name}".strip() if len(
        f"{user.first_name}{user.last_name}".strip()) > 0 else user.username


def _createOrGetUserDataByGoogleUserInfo(userinfo):
    userdata = Userdata(name=userinfo['name'], picture=userinfo['picture'], email=userinfo['email'])
    social_account = SocialAccount.objects.filter(uid=userinfo['sub']).values('user_id')
    if len(social_account) < 1:
        first_name = last_name = ''
        if " " in userinfo['name']:
            first_name = userinfo['name'].split(" ", 1)[0]
            last_name = userinfo['name'].split(" ", 1)[1]
        user = User.objects.create_user(
            username=utils.generate_unique_username(
                txts=[userinfo['email'], userinfo['given_name'], userinfo['family_name'],
                      userinfo['name']]),
            email=userinfo['email'],
            password=User.objects.make_random_password(),
            last_login=datetime.datetime.now(),
            last_name=last_name,
            first_name=first_name,
        )
        SocialAccount.objects.create(**{
            'provider': 'google',
            'uid': userinfo['sub'],
            'user_id': user.id,
            'extra_data': userinfo,
        })
        user_id = user.id
        userdata.username = user.username
    else:
        user_id = social_account[0]['user_id']
        userdata.username = User.objects.filter(pk=user_id).values('username')[0]['username']
    if userdata.name.strip() == "":
        userdata.name = userdata.username
    token, created = Token.objects.get_or_create(user_id=user_id)
    userdata.token = token.key
    return userdata

    # return data


@dataclass
class Userdata:
    username: str = ''
    name: str = ''
    picture: str = ''
    email: str = ''
    token: str = ''

    def dict(self):
        if not self.username or not self.name or not self.email:
            raise ValueError()
        return asdict(self)
