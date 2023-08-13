import inspect
import json

from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.models import TuyaDevices, TuyaHomes, TuyaDeviceFunctions, TuyaDeviceRemotekeys
from main.views import get_TuyaCloudClient


class DevicesRemotesLoadViewSet(viewsets.ViewSet):
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
        res = self.load_device_remotes(user_id, tcc)
        return Response(res)

    def load_device_remotes(self, user_id, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        # найти все объекты в базе с wnykq
        devices_wnykq = TuyaDevices.objects.filter(
            home_id__in=TuyaHomes.objects.filter(user=user_id).values('home_id'), category='wnykq'
        ).values('device_id')
        result['devices'] = json.dumps(list(devices_wnykq))
        # для каждого wnykq запросить список пультов
        cols = [f.name for f in TuyaDeviceRemotekeys._meta.fields]
        while devices_wnykq:
            device = devices_wnykq[0]
            remotes = tcc.get_subdevices(device['device_id'])
            # todo: для каждого qt получить список команд и положить в базу insert-or-update
            while remotes:
                remote_id = remotes.pop()['id']
                result['msgs'].append(f"got remote_id {remote_id}")
                resp = tcc.get_remote_control_keys(device['device_id'], remote_id)
                row = {k: resp[k] for k in cols if k in resp}
                row['parent_id'] = device['device_id']
                row['payload'] = resp
                obj, is_obj_created = TuyaDeviceRemotekeys.objects.update_or_create(
                    pk=remote_id, defaults=row
                )
                result['msgs'].append(
                    f'remote_control_keys record {remote_id} {"created" if is_obj_created else "updated"}')
            devices_wnykq = devices_wnykq.exclude(device_id=device["device_id"])
        return result

class DevicesFunctionsLoadViewSet(viewsets.ViewSet):
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
        res = self.load_device_functions(user_id, tcc)
        return Response(res)

    def load_device_functions(self, user_id, tcc):
        result = {'success': True, 'msgs': [], 'data': []}

        devices = TuyaDevices.objects.filter(
            home_id__in=TuyaHomes.objects.filter(user=user_id).values('home_id')
        ).values('device_id', 'product_id', 'payload', 'category')
        while devices:
            device = devices[0]
            resp = tcc.get_device_functions(device['device_id'])
            cols = [f.name for f in TuyaDeviceFunctions._meta.fields]
            row = {k: resp[k] for k in cols if k in resp}
            row['product_id'] = device['product_id']
            row['status'] = device['payload']['status']
            row['category'] = device['category']
            row['payload'] = resp
            if not 'functions' in row:
                row['functions'] = []
            elif type(row['functions']) == list:
                for k in range(len(row['functions'])):
                    if row['functions'][k]['values']:
                        try:
                            row['functions'][k]['values'] = json.loads(row['functions'][k]['values'])
                        except (TypeError, ValueError):
                            pass
            if type(row['status']) == list:
                for k in range(len(row['status'])):
                    if row['status'][k]['value']:
                        try:
                            row['status'][k]['value'] = json.loads(row['status'][k]['value'])
                            # result['msgs'].append(f"{row['product_id']} json value status found")
                        except (TypeError, ValueError):
                            pass
            function_codes = []
            if 0 < len(row['functions']):
                function_codes = [row['functions'][j]['code'] for j in range(len(row['functions']))]
            if 0 < len(row['status']):
                for st in row['status']:
                    if st['code'] not in function_codes:
                        row['functions'].append({
                            'code': st['code'],
                            'desc': st['code'],
                            'name': st['code'],
                            'type': "Readonly",
                            'values': {}
                        })
            if not TuyaDeviceFunctions.objects.filter(product_id=device['product_id']).exists():
                obj = TuyaDeviceFunctions.objects.create(**row)
                result['msgs'].append(f'record {device["product_id"]} created')
            else:
                result['msgs'].append(f'record {device["product_id"]} skipped')
            devices = devices.exclude(product_id=device["product_id"])
        return result


class DevicesLoadViewSet(viewsets.ViewSet):
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
        res = self.load_devices(user_id, tcc)
        return Response(res)

    def load_devices(self, user_id, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        cols = [f.name for f in TuyaDevices._meta.fields]
        for device in tcc.get_user_devices():
            row = {k: device[k] for k in cols if k in device}
            row['icon_url'] = 'https://' + tcc.ENDPOINT_URL.replace('openapi', 'images') + '/' + device['icon']
            row['payload'] = device
            row['home_id'] = device['owner_id']
            row['device_id'] = device['id']
            obj, is_obj_created = TuyaDevices.objects.update_or_create(
                pk=device['uuid'], defaults=row
            )
            result['msgs'].append(f'record {row["uuid"]} {"created" if is_obj_created else "updated"}')
        return result


class DevicesViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        if 'device_uuid' not in kw or 'cmd' not in kw:
            return Response(None, status.HTTP_400_BAD_REQUEST)

        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            return Response('invalid tuya credentials', status.HTTP_422_UNPROCESSABLE_ENTITY)
        match kw['cmd']:
            case 'status':
                res = self.get_device_status(user_id, kw['device_uuid'], tcc)
            case _:
                return Response(None, status.HTTP_400_BAD_REQUEST)
        return Response(res)

    def put(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        if 'device_uuid' not in kw or 'cmd' not in kw:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            return Response('invalid tuya credentials', status.HTTP_422_UNPROCESSABLE_ENTITY)
        match kw['cmd']:
            case 'status':
                res = self.set_device_status(user_id, kw['device_uuid'], request.data, tcc)
            case 'rcc':
                Response(request.data)
                res = self.send_rcc(user_id, kw['device_uuid'], request.data, tcc)
            case _:
                return Response(None, status.HTTP_400_BAD_REQUEST)
        return Response(res)

    def set_device_status(self, user_id, device_uuid, req, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {device_uuid}")
        commands = []
        for key in list(req.keys()):
            commands.append({
                "code": key,
                "value": req[key]
            })
        exec = {"commands": commands}
        result['data'] = tcc.exec_device_command(device_uuid, exec)
        return result

    def get_device_status(self, user_id, device_uuid, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {device_uuid}")
        resp_raw = tcc.get_device_status(device_uuid)
        result['data'] = {}
        if list == type(resp_raw):
            for k in range(len(resp_raw)):
                result['data'][resp_raw[k]['code']] = resp_raw[k]['value']
        return result

    def send_rcc(self, user_id, device_uuid, req, tcc):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {device_uuid}")
        command = {
            "category_id": req['category_id'],
            "remote_index": req['remote_index'],
            "key": req['key'],
            "key_id": req['key_id']
        }
        result['data'] = tcc.send_remote_control_command(device_uuid, req['remote_uuid'], command)
        if not result['data']:
            result['data'] = 'sent'

        return result
