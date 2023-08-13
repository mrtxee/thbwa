from dataclasses import dataclass, asdict

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.models import TuyaDeviceFunctions, TuyaDevices, TuyaHomeRooms, TuyaHomes
from main.views import get_TuyaCloudClient


class NotImplementedViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response(None, status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kw):
        return Response(request.data, status.HTTP_501_NOT_IMPLEMENTED)


class HomesLoadViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        return Response(None, status.HTTP_400_BAD_REQUEST)
    def put(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        res = self.load_homes(user_id)
        return Response(res)

    def load_homes(self, user_id):
        result = {'success': True, 'msgs': [], 'data': []}
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            result['success'] = False
            result['msgs'].append(f"Exception: {str(e)}")
            return JsonResponse(result)
        # убираем у этого пользователя все ссылки на дома
        User.objects.get(id=user_id).tuyahomes_set.clear()
        result['msgs'].append(f'homes m2m relation truncated for {user_id}')
        homes = tcc.get_user_homes()
        cols = [f.name for f in TuyaHomes._meta.fields]

        for home in homes:
            row = {k: home[k] for k in cols if k in home}
            row['home_id'] = int(row['home_id'])
            row['payload'] = home
            if TuyaHomes.objects.filter(home_id=home["home_id"]).exists():
                if not TuyaHomes.objects.filter(user=user_id, home_id=home["home_id"]).exists():
                    # если дом есть, но пользователя в нем нет, добавляем его в дом
                    obj = TuyaHomes.objects.get(home_id=home["home_id"])
                    obj.user.add(user_id)
                    result['msgs'].append(f'record {int(user_id) * 99} joined {home["home_id"]}')
                TuyaHomes.objects.filter(user=user_id, home_id=home["home_id"]).update(**row)
                result['msgs'].append(f'record cau.{home["home_id"]} updated')
            else:
                obj = TuyaHomes.objects.create(**row)
                obj.user.add(user_id)
                result['msgs'].append(f'record cau.{home["home_id"]} created')
        return result


class HomesViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id

        context = self.fetchHomes(user_id)
        response = Response(context)
        return response

    def fetchHomes(self, user_id):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"rui = {user_id}")

        homes = TuyaHomes.objects.filter(user=user_id).values('home_id', 'name', 'geo_name')
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