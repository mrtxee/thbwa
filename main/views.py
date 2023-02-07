import json
import logging
from logging.handlers import RotatingFileHandler
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
import inspect
import tuyacloud
from .models import UserSettings, UserSettingsForm, TuyaHomes, TuyaHomeRooms, TuyaDevices, TuyaDeviceFunctions
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(settings.BASE_DIR, '.env')
load_dotenv(dotenv_path)
from django.shortcuts import HttpResponseRedirect


# noinspection DuplicatedCode
def api(request, ACTION=None, USER_ID=None):
    result = {'success': True, 'msgs': [], 'data': []}
    if not ACTION or not USER_ID:
        result['success'] = False
        result['msgs'].append("bad query")
        return JsonResponse(result)
    else:
        result['msgs'].append(f"do {ACTION} for {USER_ID}")

    match ACTION:
        case "del_homes":
            TuyaHomes.objects.filter(user=USER_ID).delete()
            result['msgs'].append('homes truncated')
            # v = TuyaHomes.objects.filter(user=USER_ID).values('home_id')
            # result['msgs'].append(list(v))

        case "load_homes":
            try:
                tcc = get_TuyaCloudClient(USER_ID)
            except (KeyError, TypeError) as e:
                result['success'] = False
                result['msgs'].append(f"Exception: {str(e)}")
                return JsonResponse(result)
            TuyaHomes.objects.filter(user=USER_ID).delete()
            result['msgs'].append('homes truncated')

            homes = tcc.get_user_homes()
            cols = [f.name for f in TuyaHomes._meta.fields]

            for home in homes:
                row = {k: home[k] for k in cols if k in home}
                row['home_id'] = int(row['home_id'])
                row['payload'] = home

                if TuyaHomes.objects.filter(user=USER_ID, home_id=home["home_id"]).exists():
                    TuyaHomes.objects.filter(user=USER_ID, home_id=home["home_id"]).update(**row)
                    result['msgs'].append(f'record {USER_ID}.{home["home_id"]} updated')
                else:
                    obj = TuyaHomes.objects.create(**row)
                    obj.user.add(USER_ID)
                    result['msgs'].append(f'record {USER_ID}.{home["home_id"]} created')
        case "load_rooms":
            homes = TuyaHomes.objects.filter(user=USER_ID).values('home_id')
            if 1 > homes.count():
                result['success'] = False
                result['msgs'].append(f"no homes found")
                return JsonResponse(result)
            try:
                tcc = get_TuyaCloudClient(USER_ID)
            except (KeyError, TypeError) as e:
                result['success'] = False
                result['msgs'].append(f"Exception: {str(e)}")
                return JsonResponse(result)

            TuyaHomeRooms.objects.filter(home_id__in=homes).delete()
            result['msgs'].append('rooms truncated')

            for h in homes:
                home_id = h['home_id']
                rooms = tcc.get_home_rooms(home_id)['rooms']
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
        case "load_devices":
            try:
                tcc = get_TuyaCloudClient(USER_ID)
            except (KeyError, TypeError) as e:
                result['success'] = False
                result['msgs'].append(f"Exception: {str(e)}")
                return JsonResponse(result)
            # LOAD ALL DEVICES TO L_DB
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
        case "set_device_rooms":
            home_ids = TuyaHomes.objects.filter(user=USER_ID).values('home_id')
            TuyaDevices.objects.filter(home_id__in=home_ids).update(
                room_id=None)
            result['msgs'].append(f"'{str(list(home_ids))} house devices set room to null")
            rooms = TuyaHomeRooms.objects.filter(home_id__in=home_ids).values('room_id', 'home_id')
            if 1 > rooms.count():
                result['success'] = False
                result['msgs'].append(f"no rooms found")
                return JsonResponse(result)
            try:
                tcc = get_TuyaCloudClient(USER_ID)
            except (KeyError, TypeError) as e:
                result['success'] = False
                result['msgs'].append(f"Exception: {str(e)}")
                return JsonResponse(result)
            for room in rooms:
                logger.debug(f"apply for {room['home_id']}.{room['room_id']}")
                room_devices = tcc.get_room_devices(room['home_id'], room['room_id'])
                room_devices_uuid_list = [room_devices[k]['uuid'] for k in range(len(room_devices))]
                TuyaDevices.objects.filter(uuid__in=room_devices_uuid_list).update(room_id=room['room_id'])
                result['msgs'].append(f"'{str(room_devices_uuid_list)} set to room {room['room_id']}")
        case "get_devices":
            homes = TuyaHomes.objects.filter(user=USER_ID).values('home_id', 'name', 'geo_name')
            for home in homes:
                rooms = list(TuyaHomeRooms.objects.filter(home_id=home['home_id']).values('home_id', 'room_id', 'name'))
                rooms.append({
                    'room_id': None,
                    'home_id': home['home_id'],
                    'name': 'default'
                })

                home['rooms'] = []
                for room in rooms:
                    devices = list(TuyaDevices.objects.filter(
                        room_id=room['room_id'], home_id=room['home_id']
                    ).values('name', 'icon_url', 'category', 'device_id', 'product_id'))

                    for k in range( len(devices) ):
                        dfk = list( TuyaDeviceFunctions.objects.filter( product_id = devices[k]['product_id'] )
                           .values('functions', 'status') )
                        if dfk:
                            devices[k] = devices[k] | dfk[0]
                        else:
                            devices[k]['functions'] = []
                            devices[k]['status'] = []
                        # if devices[k]['functions'] == [] and devices[k]['status'] == []:
                        #     result['msgs'].append(f"skip passive device {devices[k]['device_id']}")

                    room['devices'] = [d for d in devices if d['functions'] and d['status'] ]

                    if 0 < len(room['devices']):
                        if not room['room_id']:
                            room['room_id'] = 10 * room['home_id']
                        home['rooms'].append(room)

                result['data'].append(home)
                result['msgs'].append(home['home_id'])

        case "load_device_functions":
            try:
                tcc = get_TuyaCloudClient(USER_ID)
            except (KesyError, TypeError) as e:
                result['success'] = False
                result['msgs'].append(f"Exception: {str(e)}")
                return JsonResponse(reult)

            devices = TuyaDevices.objects.filter(
                home_id__in=TuyaHomes.objects.filter(user=USER_ID).values('home_id')
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
                            row['functions'][k]['values'] = json.loads(row['functions'][k]['values'])

                if type(row['status']) == list:
                    for k in range( len(row['status']) ):
                        if row['status'][k]['value']:
                            try:
                                row['status'][k]['value'] = json.loads(row['status'][k]['value'])
                                #result['msgs'].append(f"{row['product_id']} json value status found")
                            except (TypeError, ValueError) :
                                pass

                function_codes = []
                if 0<len(row['functions']):
                    function_codes = [ row['functions'][j]['code'] for j in range( len(row['functions']) ) ]
                if 0<len(row['status']):
                    for st in row['status']:
                        if st['code'] not in function_codes:
                            row['functions'].append({
                                'code' : st['code'],
                                'desc' : st['code'],
                                'name' : st['code'],
                                'type' : "Readonly",
                                'values' : {}
                            })
                # if len(status_codes) > len(function_codes):
                #     result['msgs'].append(f"{row['product_id']} status-functions ISSUE")
                #     result['msgs'].append(str(function_codes))
                #     result['msgs'].append(str(status_codes))

                if not TuyaDeviceFunctions.objects.filter(product_id=device['product_id']).exists():
                    obj = TuyaDeviceFunctions.objects.create(**row)
                    result['msgs'].append(f'record {device["product_id"]} created')
                else:
                    result['msgs'].append(f'record {device["product_id"]} skipped')
                devices = devices.exclude(product_id=device["product_id"])
        case _:
            result['success'] = False
            result['msgs'].append(f"unknown action: {ACTION} on {USER_ID}")
    return JsonResponse(result)

def api_get_device_functions(request, USER_ID=None, DEVICE_UUID=None):
    #http://localhost:8000/api/v1.0/get_device_status/2/08003658d8bfc0522706
    result = {'success': True, 'msgs': [], 'data': []}
    if not DEVICE_UUID or not USER_ID:
        result['success'] = False
        result['msgs'].append("bad query")
        return JsonResponse(result)
    else:
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {USER_ID}.{DEVICE_UUID}")
    try:
        tcc = get_TuyaCloudClient(USER_ID)
    except (KeyError, TypeError) as e:
        result['success'] = False
        result['msgs'].append(f"Exception: {str(e)}")
        return JsonResponse(result)
    result['data'] = tcc.get_device_functions(DEVICE_UUID)

    if type(result['data']['functions']) == list:
        for k in range( len( result['data']['functions'] ) ):
            if result['data']['functions'][k]['values'] :
                result['data']['functions'][k]['values'] = json.loads(result['data']['functions'][k]['values'])

    return JsonResponse(result)

def api_get_device_status(request, USER_ID=None, DEVICE_UUID=None):
    result = {'success': True, 'msgs': [], 'data': []}
    if not DEVICE_UUID or not USER_ID:
        result['success'] = False
        result['msgs'].append("bad query")
        return JsonResponse(result)
    else:
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {USER_ID}.{DEVICE_UUID}")
    try:
        tcc = get_TuyaCloudClient(USER_ID)
    except (KeyError, TypeError) as e:
        result['success'] = False
        result['msgs'].append(f"Exception: {str(e)}")
        return JsonResponse(result)
    resp_raw = tcc.get_device_status(DEVICE_UUID)

    result['data'] = {}
    if list == type(resp_raw):
        for k in range(len(resp_raw)):
            result['data'][resp_raw[k]['code']]=resp_raw[k]['value']

    return JsonResponse(result)

def api_set_device_status(request, USER_ID=None, DEVICE_UUID=None):
    #http://localhost:8000/api/v1.0/set_device_status/2/08003658d8bfc0522706
    result = {'success': True, 'msgs': [], 'data': []}
    if not DEVICE_UUID or not USER_ID:
        result['success'] = False
        result['msgs'].append("bad query")
        return JsonResponse(result)
    else:
        result['msgs'].append(f"do {inspect.stack()[0][3]} for {USER_ID}.{DEVICE_UUID}")

    # exec0 = {
    #         "commands": [
    #             {
    #                 "code": "switch_led",
    #                 "value": True
    #             },
    #             {
    #                 "code": "bright_value",
    #                 "value": 30
    #             }
    #         ]
    #     }
    req = json.loads(request.body.decode('utf-8'))
    commands = []
    for key in list(req.keys()):
        commands.append({
            "code": key,
            "value": req[key]
        })
    exec = {"commands": commands}
    #result['exec']=commands
    #result['msgs'].append(exec0)

    try:
        tcc = get_TuyaCloudClient(USER_ID)
    except (KeyError, TypeError) as e:
        result['success'] = False
        result['msgs'].append(f"Exception: {str(e)}")
        return JsonResponse(result)
    result['data'] = tcc.exec_device_command(DEVICE_UUID, exec)
    result['data0'] = exec

    return JsonResponse(result)

# todo: see object_factory for django.py

def singleton(class_):
    instances = {}

    # д.б. статик метод
    #
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class TuyaCloudClientNicerSingleton(tuyacloud.TuyaCloudClientNicer):
    pass


def get_TuyaCloudClient(uid: int) -> object:
    if 1 != UserSettings.objects.filter(pk=uid).count():
        raise TypeError("bad settings provided")

    user_settings = UserSettings.objects.filter(pk=uid).values()[0]
    try:
        tcc = TuyaCloudClientNicerSingleton(
            ACCESS_ID=user_settings['access_id'],
            ACCESS_SECRET=user_settings['access_secret'],
            UID=user_settings['uid'],
            ENDPOINT_URL=user_settings['endpoint_url']
        )
    except KeyError:
        raise KeyError("bad tuya settings provided")
    return tcc

def devices(request):
    if request.user.is_authenticated:
        head_includes = '<script defer="defer" src="/static/js/main.%s.js" bbu="%s" ui="%s"></script>' % (
        'd1605714', os.environ.get("BACKEND_BASE_URL"), request.user.id)
        head_includes += '<link href="/static/css/main.ff179a16.css" rel="stylesheet">'
        context = {
            'head_includes': head_includes
        }
        return render(request, "devices.html", context=context)
    else:
        #return HttpResponse("<h1>login please</h1>")
        return HttpResponseRedirect("/accounts/login/")

def about(request):
    context = {
        "terminal": ""
    }
    return render(request, "about.html", context=context)

def faq(request):
    return render(request, "faq.html")

def user_profile(request):
    context = {'form': UserSettingsForm(request.POST or None)}

    if request.method == 'POST':
        # add or update record
        if context['form'].is_valid():
            cols = [f.name for f in UserSettings._meta.fields]
            row = {k: request.POST[k] for k in cols if k in request.POST}
            obj, is_obj_created = UserSettings.objects.update_or_create(
                user_id=request.user.id, defaults=row
            )
            logger.debug(f'is_obj_created {is_obj_created}; obj {obj}')
            context['success_updated_alert'] = True
        else:
            context['fill_form_alert'] = True
    else:
        if UserSettings.objects.filter(pk=request.user.id).exists():
            context['form'] = UserSettingsForm(instance=UserSettings.objects.get(pk=request.user.id))
    return render(request, "user/profile.html", context)


def set_logger():
    logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logger_file_handler = logging.FileHandler(f'{__name__}.log')
    logger_file_handler = logging.handlers.RotatingFileHandler(f'{__name__}.log', maxBytes=51200, backupCount=2)
    # logger_file_handler.setLevel(logging.DEBUG)
    logger_file_handler.setFormatter(logger_formatter)
    logger1 = logging.getLogger(__name__)
    logger1.setLevel(logging.DEBUG)
    logger1.addHandler(logger_file_handler)
    # logger1.info(f"{__file__} updated")
    logger_tuya_cloud_client = logging.getLogger('tuyacloud.TuyaCloudClient')
    logger_tuya_cloud_client.setLevel(logging.DEBUG)
    logger_tuya_cloud_client.addHandler(logger_file_handler)
    logger1.info(f"F_HANDLERS: {str(logging.handlers)}")
    return logger1

logger = set_logger()