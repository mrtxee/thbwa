import datetime
import json

import requests
from allauth import utils
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

CLIENT_ID = '93483542407-ckrg8q5q527dmcd62ptg0am5j9jhvesb.apps.googleusercontent.com'


class AuthLoginViewSet(viewsets.ViewSet):
    def list1(self, request, *args, **kw):
        pass

    def list(self, request, *args, **kw):
        data = {'user': 'data'}
        data['token_is'] = '222'
        data['HTTP_AUTHORIZATION'] = request.META["HTTP_AUTHORIZATION"]
        #check is conains 'Token'
        if not 'Token ' in request.META["HTTP_AUTHORIZATION"]:
            return Response(None, status.HTTP_403_FORBIDDEN)
        # check token exists
        if not Token.objects.filter(key=request.META["HTTP_AUTHORIZATION"].split()[1]).exists():
            return Response(None, status.HTTP_401_UNAUTHORIZED)
        user = Token.objects.get(key=request.META["HTTP_AUTHORIZATION"].split()[1]).user
        social_account = SocialAccount.objects.filter(user_id=user.id).values('extra_data')
        if len(social_account) < 1:
            return Response(None, status.HTTP_401_UNAUTHORIZED)
        data = {
            'name': social_account[0]["extra_data"]["name"],
            'username': user.username,
            'picture': social_account[0]["extra_data"]["picture"],
            'email': social_account[0]["extra_data"]["email"],
        }
        response = JsonResponse(data)
        return response


class AuthLoginGoogleViewSet(viewsets.ViewSet):
    def create(self, request):
        requestBodyJson = json.loads(request.body)
        return JsonResponse(createOrGetUserDataByGoogleUserInfo(
            requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
                'Authorization': f'{requestBodyJson["token_type"]} {requestBodyJson["access_token"]}'}).json()))


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response(None, status.HTTP_401_UNAUTHORIZED)


def createOrGetUserDataByGoogleUserInfo(userinfo):
    data = {
        'name': userinfo['name'],
        'username': '',
        'picture': userinfo['picture'],
        'email': userinfo['email'],
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
