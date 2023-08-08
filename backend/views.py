from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from backend.serializers import UserSerializer, TuyaHomesSerializer
from main.models import TuyaHomes, TuyaHomeRooms, TuyaDevices, TuyaDeviceFunctions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated() and request.user.is_admin
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False
    # def has_object_permission(self, request, view, obj):
    #     # Deny actions on objects if the user is not authenticated
    #     if not request.user.is_authenticated():
    #         return False
    #     if view.action == 'retrieve':
    #         return obj == request.user or request.user.is_admin
    #     elif view.action in ['update', 'partial_update']:
    #         return obj == request.user or request.user.is_admin
    #     elif view.action == 'destroy':
    #         return request.user.is_admin
    #     else:
    #         return False


# https://django.fun/ru/docs/django-rest-framework/3.12/api-guide/authentication/

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


class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)


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
