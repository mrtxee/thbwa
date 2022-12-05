import json
import logging
from logging.handlers import RotatingFileHandler
from django.http import JsonResponse
from django.shortcuts import render
import tuyacloud
from .models import UserSettings, UserSettingsForm, TuyaHomes, TuyaHomeRooms, TuyaDevices


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
            #v = TuyaHomes.objects.filter(user=USER_ID).values()
            #result['msgs'].append(list(v))

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
                rooms = TuyaHomeRooms.objects.filter(home_id=home['home_id']).values('home_id', 'room_id', 'name')
                # home['rooms'] = [rooms[k] for k in range(rooms.count())]
                home['rooms'] = []
                for room in rooms:
                    room['devices'] = list(TuyaDevices.objects.filter(
                        room_id=room['room_id']
                    ).values('name', 'icon_url', 'category', 'uuid'))

                    home['rooms'].append(room)
                result['data'].append(home)
                result['msgs'].append(home['home_id'])
        case "get_devices_line":
            homes = TuyaHomes.objects.filter(user=USER_ID).values('home_id', 'name', 'geo_name')
            homes_ids = [homes[k]['home_id'] for k in range(homes.count())]
            rooms = TuyaHomeRooms.objects.filter(
                home_id__in=homes_ids
            ).values('home_id', 'room_id', 'name')

            devices = TuyaDevices.objects.filter(
                owner_id__in=homes_ids
            ).values('name', 'icon_url', 'category', 'uuid', 'room_id', 'owner_id')
            result['data'] = {
                'homes': list(homes),
                'rooms': list(rooms),
                'devices': list(devices)
            }

            result['msgs'].append(f"homes available {homes.count()}")
            result['msgs'].append(f"rooms available {rooms.count()}")
            result['msgs'].append(f"devices available {devices.count()}")
        case _:
            result['success'] = False
            result['msgs'].append(f"unknown action: {ACTION} on {USER_ID}")
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
    return render(request, "user_profile.html", context)


def user_playground(request):
    context = {
        'settings': 'settings',
        'houses': 'houses',
        'rooms': 'rooms',
        'devices': 'devices',
    }
    if UserSettings.objects.filter(pk=request.user.id).exists():
        # settings = User_settings.objects.get(pk=request.user.id)
        settings_dict = UserSettings.objects.filter(pk=request.user.id).values()[0]
        # user_settigns =
        # context['settings'] = serializers.serialize('json', [ settings ])
        context['settings'] = f'SETTINGS: {str(settings_dict)}'

        tcc = get_TuyaCloudClient(4)

        result = tcc.get_user_homes()
        print("get_user_homes:\n", json.dumps(result, indent=3, ensure_ascii=False))
    else:
        context['no_settings_alert'] = True

    return render(request, "user_playground.html", context)


def devices(request):
    return render(request, "devices.html")


def menu(request):
    context = {
        "terminal": str(request.user),
        # "user" : request.user
    }
    return render(request, "index.html", context=context)


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
