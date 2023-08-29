import datetime
import json
import os
from dataclasses import dataclass, asdict

import requests
from allauth import utils
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str, url_str_to_user_pk
from allauth.socialaccount.models import SocialAccount
from dacite import from_dict
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.http import JsonResponse
from dotenv import load_dotenv
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.models import UserSettings
from thbwa import settings

dotenv_path = os.path.join(settings.BASE_DIR, '.env')
load_dotenv(dotenv_path)


class NewPasswordViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        if 'username' not in request.data or 'password' not in request.data:
            return Response(None, status.HTTP_403_FORBIDDEN)
        user = authenticate(request, username=request.data['username'], password=request.data['old_password'])
        if not user:
            return Response('bad credentials', status.HTTP_401_UNAUTHORIZED)
        token_user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        if request.data['username'] != user.username or user.id != token_user_id:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data['password'])
        user.save()
        return Response()


class ResetPasswordViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'email' not in request.data:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=request.data['email']).exists():
            return Response('email is not registered', status.HTTP_417_EXPECTATION_FAILED)

        user = User.objects.get(email=request.data['email'])
        email = request.data['email']

        url = os.environ.get("FRONTEND_BASE_URL") + '/resetpass/' + user_pk_to_url_str(
            user) + '-' + default_token_generator.make_token(user)

        context = {"current_site": get_current_site(request),
                   "user": user,
                   "password_reset_url": url,
                   "request": request}
        get_adapter(request).send_mail(
            'account/email/password_reset_key',
            email,
            context)
        # todo: add username reminder
        return Response(None, status.HTTP_200_OK)

    def put(self, request, *args, **kw):
        if 'key' not in request.data or 'password' not in request.data:
            return Response(None, status.HTTP_400_BAD_REQUEST)

        user_pk_url_str, token = request.data['key'].split('-', maxsplit=1)
        user = User.objects.get(pk=url_str_to_user_pk(user_pk_url_str))
        if not default_token_generator.check_token(user, token):
            return Response('bad token', status.HTTP_400_BAD_REQUEST)

        user.set_password(request.data['password'])
        user.save()

        return Response(None, status.HTTP_200_OK)


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
        userdata = UserLoginData(username=request.data['username'],
                                 name=f"{request.data['last_name']} {request.data['first_name']}"
                                 )
        userdata.token = Token.objects.get_or_create(user_id=user.id)[0].key
        return JsonResponse(userdata.dict())


class UserViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        user_data = UserData()
        if User.objects.filter(pk=user_id).exists():
            user = User.objects.filter(pk=user_id)
            user_data = from_dict(UserData, json.loads(serializers.serialize("json", user))[0]['fields'])
        return JsonResponse(user_data.dict())

    def create(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        obj = User.objects.filter(id=user_id).update(**request.data)
        return Response()


class UserSettingsViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user
        user_settings_data = UserSettingsData()
        if UserSettings.objects.filter(user_id=user.id).exists():
            user_settings = UserSettings.objects.filter(user_id=user.id)
            user_settings_data = from_dict(UserSettingsData,
                                           json.loads(serializers.serialize("json", user_settings))[0]['fields'])
        return JsonResponse(user_settings_data.dict())

    def create(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        obj, created = UserSettings.objects.update_or_create(user_id=user_id, defaults=request.data)
        return Response()


class LoginViewSet(viewsets.ViewSet):
    def create(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response(None, status.HTTP_403_FORBIDDEN)
        user = authenticate(request, username=request.data['username'], password=request.data['password'])
        if not user:
            return Response('bad credentials', status.HTTP_401_UNAUTHORIZED)
        userdata = UserLoginData(username=user.username)
        social_account = SocialAccount.objects.filter(uid=user.id).values('user_id')
        if len(social_account) < 1:
            userdata.set_name_by_user(user)
        else:
            userdata.name = social_account[0]["extra_data"]["name"]
            userdata.picture = social_account[0]["extra_data"]["picture"]
        userdata.token = Token.objects.get_or_create(user_id=user.id)[0].key
        return Response(userdata.dict())

    # todo: проверка, что такой имэйл еще не занят

    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user
        social_account = SocialAccount.objects.filter(user_id=user.id).values('extra_data')
        userdata = UserLoginData(username=user.username)
        if len(social_account) > 0:
            userdata.name = social_account[0]["extra_data"]["name"]
            userdata.picture = social_account[0]["extra_data"]["picture"]
        else:
            userdata.set_name_by_user(user)
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
        userdata = UserLoginData(name=userinfo['name'], picture=userinfo['picture'])
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


@dataclass
class UserLoginData:
    username: str = ''
    name: str = ''
    picture: str = ''
    token: str = ''

    def set_name_by_user(self, user):
        self.name = f"{user.first_name} {user.last_name}".strip() if len(
            f"{user.first_name}{user.last_name}".strip()) > 0 else user.username

    def dict(self):
        if not self.username or not self.name:
            raise ValueError()
        return asdict(self)


@dataclass
class UserData():
    username: str = ''
    last_login: str = ''
    date_joined: str = ''
    last_name: str = ''
    email: str = ''
    first_name: str = ''

    def dict(self):
        self.date_joined = self.date_joined.split('T')[0] if 'T' in self.date_joined else self.date_joined
        self.last_login = self.last_login.split('T')[0] if 'T' in self.last_login else self.last_login
        if not self.username:
            raise ValueError()
        return asdict(self)


@dataclass
class UserSettingsData:
    access_id: str = ''
    access_secret: str = ''
    uid: str = ''
    endpoint_url: str = ''

    def dict(self):
        return asdict(self)
