import inspect

from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from main.views import get_TuyaCloudClient


class DevicesViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        if 'device_uuid' not in kw:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        res = self.get_device_status(user_id, kw['device_uuid'])
        return Response(res)

    def put(self, request, *args, **kw):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if 'Token ' not in request.META['HTTP_AUTHORIZATION']:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        if not Token.objects.filter(key=request.META['HTTP_AUTHORIZATION'].split()[1]).exists():
            return Response('token not exists', status.HTTP_401_UNAUTHORIZED)
        if 'device_uuid' not in kw:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        user_id = Token.objects.get(key=request.META['HTTP_AUTHORIZATION'].split()[1]).user_id
        res = self.set_device_status(user_id, kw['device_uuid'], request.data)
        return Response(res)

    def set_device_status(self, user_id, DEVICE_UUID, req):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {DEVICE_UUID}")
        commands = []
        for key in list(req.keys()):
            commands.append({
                "code": key,
                "value": req[key]
            })
        exec = {"commands": commands}
        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            result['success'] = False
            result['msgs'].append(f"Exception: {str(e)}")
            return result
        result['data'] = tcc.exec_device_command(DEVICE_UUID, exec)
        return result

    def get_device_status(self, user_id, DEVICE_UUID):
        result = {'success': True, 'msgs': [], 'data': []}
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {DEVICE_UUID}")

        try:
            tcc = get_TuyaCloudClient(user_id)
        except (KeyError, TypeError) as e:
            result['success'] = False
            result['msgs'].append(f"Exception: {str(e)}")
            return result
        resp_raw = tcc.get_device_status(DEVICE_UUID)

        result['data'] = {}
        if list == type(resp_raw):
            for k in range(len(resp_raw)):
                result['data'][resp_raw[k]['code']] = resp_raw[k]['value']
        return result
