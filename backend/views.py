import json

from django.contrib.auth.models import User
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from backend.serializers import UserSerializer, TuyaHomesSerializer
from main.models import TuyaHomes, TuyaHomeRooms, TuyaDevices, TuyaDeviceFunctions


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class TuyaHomesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TuyaHomesSerializer
    queryset = TuyaHomes.objects.all().order_by('home_id')

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user.id).values('home_id', 'name', 'geo_name')
        return query_set


""" todo: API endpoint to perform some action.
    Filtered over the current user
"""

""" todo: API endpoint to read-only result.
    Filtered over the current user
"""

CLIENT_ID = '93483542407-ckrg8q5q527dmcd62ptg0am5j9jhvesb.apps.googleusercontent.com'
SECRET = 'xxx-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'


def validateDecodeGoogleJWT(token):
    try:
        data = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        data['is_valid_token'] = True
    except ValueError:
        data['is_valid_token'] = False
    return data


class AuthLoginGoogleViewSet(ViewSet):
    def list(self, request, *args, **kw):
        context = {'google': 'login'}
        response = Response(context)
        return response

    def create(self, request):
        data = {'its': 'ok'}
        requestBodyJson = json.loads(request.body);
        if 'credential' in requestBodyJson:
            data = validateDecodeGoogleJWT(requestBodyJson['credential'])

        response = Response(data)
        return response


class HomesViewSet(ViewSet):
    def list(self, request, *args, **kw):
        context = fetchHomes(request)
        response = Response(context)
        return response


def fetchHomes(request):
    result = {'success': True, 'msgs': [], 'data': []}
    result['msgs'].append(f"rui = {request.user.id}")
    # if 1 == request.user.id:
    #     homes = TuyaHomes.objects.values('home_id', 'name', 'geo_name')
    # else:
    #     homes = TuyaHomes.objects.filter(user=request.user.id).values('home_id', 'name', 'geo_name')

    homes = TuyaHomes.objects.filter(user=request.user.id).values('home_id', 'name', 'geo_name')
    for home in homes:
        rooms = list(TuyaHomeRooms.objects.filter(home_id=home['home_id']).values('home_id', 'room_id', 'name'))
        rooms.append({
            'room_id': None,
            'home_id': home['home_id'],
            'name': 'default'
        })
        home['rooms'] = []
        for room in rooms:
            tdevices = TuyaDevices.objects.filter(room_id=room['room_id'], home_id=room['home_id']).values(
                'name', 'icon_url', 'category', 'device_id', 'product_id', 'tuyadeviceremotekeys__key_list',
                'tuyadeviceremotekeys__category_id', 'tuyadeviceremotekeys__remote_index',
                'tuyadeviceremotekeys__parent_id')
            devices = list(tdevices)
            for k in range(len(devices)):
                if devices[k]['tuyadeviceremotekeys__category_id']:
                    devices[k]["remote"] = {
                        "category_id": devices[k]['tuyadeviceremotekeys__category_id'],
                        "remote_index": devices[k]['tuyadeviceremotekeys__remote_index'],
                        "key_list": devices[k]['tuyadeviceremotekeys__key_list'],
                        "parent_id": devices[k]['tuyadeviceremotekeys__parent_id']
                    }
                dfk = list(TuyaDeviceFunctions.objects.filter(product_id=devices[k]['product_id'])
                           .values('functions', 'status'))
                if dfk:
                    devices[k] = devices[k] | dfk[0]

                if devices[k]['functions'] == [] and devices[k]['status'] == []:
                    devices[k]['status'] = [{
                        "code": "is_empty",
                        "value": True
                    }]
                elif devices[k]['functions'] == []:
                    result['msgs'].append(f"skip passive device, empty functions {devices[k]['device_id']}")
                elif devices[k]['status'] == []:
                    result['msgs'].append(f"skip passive device, empty status {devices[k]['device_id']}")
            room['devices'] = [d for d in devices if d['functions'] or d['status']]

            if 0 < len(room['devices']):
                if not room['room_id']:
                    room['room_id'] = 10 * room['home_id']
                home['rooms'].append(room)

        result['data'].append(home)
        result['msgs'].append(home['home_id'])
    return result
