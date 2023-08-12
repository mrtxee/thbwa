from dataclasses import dataclass, asdict

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.models import TuyaDeviceFunctions, TuyaDevices, TuyaHomeRooms, TuyaHomes


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


# delete that below = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
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
