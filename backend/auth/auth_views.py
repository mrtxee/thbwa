import datetime
import json
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


class AuthLoginViewSet(viewsets.ViewSet):
    def create(self, request):
        requestBodyJson = json.loads(request.body)
        if not 'username' in requestBodyJson or not 'password' in requestBodyJson:
            return Response(None, status.HTTP_403_FORBIDDEN)
        user = authenticate(request, username=requestBodyJson['username'], password=requestBodyJson['password'])
        if not user:
            return Response('bad credentials', status.HTTP_401_UNAUTHORIZED)

        userdata = Userdata(username=user.username)
        social_account = SocialAccount.objects.filter(uid=user.id).values('user_id')
        if len(social_account) < 1:
            userdata.name = user.username  # todo: fix it
            userdata.email = user.email  # todo: fix it пустоле мыло, или стандартное?
            # todo: установить в рабочей базе стандартную почту для всех
        else:
            userdata.name = social_account[0]["extra_data"]["name"];
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
        if len(social_account) < 1:
            return Response('inconsistent data', status.HTTP_406_NOT_ACCEPTABLE)
        userdata = Userdata(username=user.username,
                            name=social_account[0]["extra_data"]["name"],
                            picture=social_account[0]["extra_data"]["picture"],
                            email=social_account[0]["extra_data"]["email"])
        response = JsonResponse(userdata.dict())
        return response


class AuthLoginGoogleViewSet(viewsets.ViewSet):
    def create(self, request):
        requestBodyJson = json.loads(request.body)
        return JsonResponse(createOrGetUserDataByGoogleUserInfo(
            requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                'Authorization': f'{requestBodyJson["token_type"]} {requestBodyJson["access_token"]}'}).json()).dict())


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response('4xx test', status.HTTP_401_UNAUTHORIZED)


def createOrGetUserDataByGoogleUserInfo(userinfo):
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
