import datetime
import json

import requests
from allauth import utils
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.http import JsonResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

CLIENT_ID = '93483542407-ckrg8q5q527dmcd62ptg0am5j9jhvesb.apps.googleusercontent.com'


class AuthLoginViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        data = {'user': 'data'}
        response = JsonResponse(data)
        return response


class AuthLoginGoogleViewSet(viewsets.ViewSet):
    def create(self, request):
        requestBodyJson = json.loads(request.body)
        return JsonResponse(createOrGetUserDataByGoogleUserInfo(
            requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                'Authorization': f'{requestBodyJson["token_type"]} {requestBodyJson["access_token"]}'}).json()))


class AuthLoginGoogleUserinfoJwtViewSet(viewsets.ViewSet):
    def create(self, request):
        requestBodyJson = json.loads(request.body)
        if not 'credential' in requestBodyJson:
            return Response(None, status.HTTP_401_UNAUTHORIZED)
        data = validateDecodeGoogleJWT(requestBodyJson['credential'])
        if not data['is_valid_googlejwt']:
            return Response(None, status.HTTP_401_UNAUTHORIZED)
        return JsonResponse(createOrGetUserDataByGoogleUserInfo(data['userinfo']))
    # def list(self, request, *args, **kw):
    # def update(self, request, pk=None):
    # def partial_update(self, request, pk=None):
    # def destroy(self, request, pk=None):
    # def retrieve(self, request, pk=None):
    #     data = {'its': 'ok'}
    #     response = JsonResponse(data)
    #     return response


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        response = Response(None, status.HTTP_401_UNAUTHORIZED)
        return response


def createOrGetUserDataByGoogleUserInfo(userinfo):
    data = {
        'name': userinfo['name'],
        'username': '',
        'picture': userinfo['picture'],
        'email': userinfo['email'],
        'sub': userinfo['sub'],
    }
    social_account = SocialAccount.objects.filter(uid=userinfo['sub']).values('user_id')
    user_id = 0
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
        data['username'] = user.username
    else:
        user_id = social_account[0]['user_id']
        data['username'] = User.objects.filter(pk=user_id).values('username')[0]['username']
    if data['name'].strip() == "":
        data['name'] = data['username']
    token, created = Token.objects.get_or_create(user_id=user_id)
    data['token'] = token.key
    return data


def validateDecodeGoogleJWT(token):
    data = {
        'credentials': token,
        'userinfo': '',
        'is_valid_googlejwt': True
    }
    try:
        data['userinfo'] = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
    except ValueError:
        data['is_valid_googlejwt'] = False
    return data
