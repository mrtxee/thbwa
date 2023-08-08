import datetime
import json

from allauth import utils
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.http import JsonResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

CLIENT_ID = '93483542407-ckrg8q5q527dmcd62ptg0am5j9jhvesb.apps.googleusercontent.com'


def validateDecodeGoogleJWT(token):
    data = {
        'credentials':'',
        'is_valid_googlejwt':True
    }
    try:
        data['credentials'] = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        data['is_valid_googlejwt'] = True
    except ValueError:
        data['is_valid_googlejwt'] = False
    return data


''' DEFAULT AVATAR URL
    # 'https://' + tcc.ENDPOINT_URL.replace('openapi', 'images') + '/' + device['icon']
'''


class Test403ResponseViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        response = Response(None, status.HTTP_401_UNAUTHORIZED)
        return response

class AuthLoginGoogleViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        context = {'google': 'login'}
        response = Response(context)
        return response

    def create(self, request):
        requestBodyJson = json.loads(request.body)
        if not 'credential' in requestBodyJson:
            return Response(None, status.HTTP_401_UNAUTHORIZED)
        data = validateDecodeGoogleJWT(requestBodyJson['credential'])
        credentials = data['credentials']
        if data['is_valid_googlejwt']:
            data = {
                'name': credentials['name'],
                'username': '',
                'picture': credentials['picture'],
                'email': credentials['email'],
                'sub': credentials['sub'],
            }
            social_account = SocialAccount.objects.filter(uid=credentials['sub']).values('user_id')
            user_id = 0
            if len(social_account) < 1:
                first_name = last_name = ''
                if " " in credentials['name']:
                    first_name = credentials['name'].split(" ", 1)[0]
                    last_name = credentials['name'].split(" ", 1)[1]
                user = User.objects.create_user(
                    username=utils.generate_unique_username(txts=[credentials['email'], credentials['name']]),
                    email=credentials['email'],
                    password=User.objects.make_random_password(),
                    last_login=datetime.datetime.now(),
                    last_name=last_name,
                    first_name=first_name,
                )
                SocialAccount.objects.create(**{
                    'provider' : 'google',
                    'uid' : credentials['sub'],
                    'user_id' : user.id,
                    'extra_data' : credentials,
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
        return JsonResponse(data)

    def retrieve(self, request, pk=None):
        data = {'its': 'ok'}
        response = JsonResponse(data)
        return response

    def update(self, request, pk=None):
        data = {'its': 'ok'}
        response = JsonResponse(data)
        return response

    def partial_update(self, request, pk=None):
        data = {'its': 'ok'}
        response = JsonResponse(data)
        return response

    def destroy(self, request, pk=None):
        data = {'its': 'ok'}
        response = JsonResponse(data)
        return response
