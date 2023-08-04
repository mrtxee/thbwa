from django.contrib.auth.models import User, Group
from backend.serializers import UserSerializer, GroupSerializer, TuyaHomesSerializer, YourSerializer
from main.models import TuyaHomes, TuyaHomeRooms, TuyaDevices, TuyaDeviceFunctions

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers

class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class TuyaHomesViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
        Filtered over the current user
    """
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

class HomesViewSet(ViewSet):
    def list(self, request, *args, **kw):
        context = get_devices(request)
        response = Response(context)
        return response


def get_devices(request):
    result = {'success': True, 'msgs': [], 'data': []}

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

