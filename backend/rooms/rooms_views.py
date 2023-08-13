from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.models import TuyaHomeRooms, TuyaHomes, TuyaDevices
from main.views import get_TuyaCloudClient


class RoomsDevicesLoadViewSet(viewsets.ViewSet):
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
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            return Response('invalid tuya credentials', status.HTTP_422_UNPROCESSABLE_ENTITY)
        res = self.load_rooms_devices(user_id, tcc)
        return Response(res)

    def load_rooms_devices(self, user_id, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        home_ids = TuyaHomes.objects.filter(user=user_id).values('home_id')
        rooms = TuyaHomeRooms.objects.filter(home_id__in=home_ids).values('room_id', 'home_id')
        # result['rooms'] = list(rooms)
        if 1 > rooms.count():
            result['msgs'].append(f"there is not rooms in the house")
            return result
        else:
            TuyaDevices.objects.filter(home_id__in=home_ids).update(room_id=None)
            result['msgs'].append(f"'{str(list(home_ids))} house devices set room to null")
        for room in rooms:
            room_devices = tcc.get_room_devices(room['home_id'], room['room_id'])
            try:
                room_devices_uuid_list = [room_devices[k]['uuid'] for k in range(len(room_devices))]
                TuyaDevices.objects.filter(uuid__in=room_devices_uuid_list).update(room_id=room['room_id'])
                result['msgs'].append(f"'{str(room_devices_uuid_list)} set to room {room['room_id']}")
            except (KeyError, TypeError) as e:
                result['msgs'].append('for some device no uuid found. probably due to other owner problem')
        return result

class RoomsLoadViewSet(viewsets.ViewSet):
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
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            return Response('invalid tuya credentials', status.HTTP_422_UNPROCESSABLE_ENTITY)
        res = self.load_rooms(user_id, tcc)
        return Response(res)

    def load_rooms(self, user_id, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        homes = TuyaHomes.objects.filter(user=user_id).values('home_id')
        if 1 > homes.count():
            result['success'] = False
            result['msgs'].append(f"no homes found")
            return result
        TuyaHomeRooms.objects.filter(home_id__in=homes).delete()
        result['msgs'].append('rooms truncated')
        for h in homes:
            home_id = h['home_id']
            resp = tcc.get_home_rooms(home_id)
            rooms = None
            if 'rooms' in resp:
                rooms = resp['rooms']
            else:
                result['msgs'].append(f'no rooms found in {home_id}')
            if rooms:
                cols = [f.name for f in TuyaHomeRooms._meta.fields]
                for room in rooms:
                    row = {k: room[k] for k in cols if k in room}
                    row['home_id'] = int(home_id)
                    row['payload'] = room
                    obj, is_obj_created = TuyaHomeRooms.objects.update_or_create(
                        pk=room['room_id'], defaults=row
                    )
                    result['msgs'].append(
                        f'record {home_id}.{room["room_id"]} {"created" if is_obj_created else "updated"}')
        return result
