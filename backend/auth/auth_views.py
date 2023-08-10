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


class ResetPasswordViewSet(viewsets.ViewSet):
    def create(self, request):
        return Response(None, status.HTTP_501_NOT_IMPLEMENTED)


class UniqueUserNameCheckerViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'username' not in request.data:
            return Response('invalid input', status.HTTP_403_FORBIDDEN)
        if User.objects.filter(username=request.data['username']).exists():
            return Response(False)
        return Response(True)


class RegisterViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'username' not in request.data or 'password' not in request.data or 'email' not in request.data \
                or 'first_name' not in request.data or 'last_name' not in request.data:
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
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
        )
        userdata = Userdata(username=request.data['username'], email=request.data['email'],
                            name=f"{request.data['last_name']} {request.data['first_name']}"
                            )
        userdata.token = Token.objects.get_or_create(user_id=user.id)[0].key
        return JsonResponse(userdata.dict())


class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response(None, status.HTTP_403_FORBIDDEN)
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if not user:
            return Response('bad credentials', status.HTTP_401_UNAUTHORIZED)
        userdata = Userdata(username=user.username)
        social_account = SocialAccount.objects.filter(uid=user.id).values('user_id')
        if len(social_account) < 1:
            userdata.set_name_by_user(user)
            userdata.set_email_by_user(user)
        else:
            userdata.name = social_account[0]["extra_data"]["name"]
            userdata.picture = social_account[0]["extra_data"]["picture"]
            userdata.email = social_account[0]["extra_data"]["email"]
        userdata.token = Token.objects.get_or_create(user_id=user.id)[0].key
        return Response(userdata.dict())

    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
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
            userdata.set_name_by_user(user)
            userdata.set_email_by_user(user)
        response = JsonResponse(userdata.dict())
        return response


class LogoutEverywhereViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        data = Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).delete()
        response = Response(data)
        return response


class LoginGoogleViewSet(viewsets.ViewSet):
    def create(self, request):

        return JsonResponse(self._get_userdata_by_google_userinfo(
            requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                'Authorization': f'{request.data["token_type"]} {request.data["access_token"]}'}).json()).dict())

    def _get_userdata_by_google_userinfo(self, userinfo):
        userdata = Userdata(name=userinfo['name'], picture=userinfo['picture'], email=userinfo['email'])
        social_account = SocialAccount.objects.filter(uid=userinfo['sub']).values('user_id')
        if len(social_account) < 1:
            user = self._get_created_user(userinfo)
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

    def _get_created_user(self, userinfo):
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
        return user


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response('4xx test', status.HTTP_401_UNAUTHORIZED)


@dataclass
class Userdata:
    username: str = ''
    name: str = ''
    picture: str = ''
    email: str = ''
    token: str = ''

    def set_name_by_user(self, user):
        self.name = f"{user.first_name} {user.last_name}".strip() if len(
            f"{user.first_name}{user.last_name}".strip()) > 0 else user.username

    def set_email_by_user(self, user):
        self.email = user.email if len(user.email.strip()) > 0 else f"{user.username}@mailto.plus"

    def dict(self):
        if not self.username or not self.name or not self.email:
            raise ValueError()
        return asdict(self)
