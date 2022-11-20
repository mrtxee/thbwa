import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

import tuyacloud
from .models import UserSettings, UserSettingsForm, TuyaHomes


def api(request, action=None, action_id=None):
    result = {
        'success': True,
        'data': {}
    }
    result['data']['msgs'] = []
    if not action or not action_id:
        result['success'] = False
        result['data']['msgs'].append("bad query")
        return JsonResponse(result)

    match action:
        case "truncate_devices":
            result['data']['msgs'].append(f"do {action} for {action_id}")
        case "reload_devices":
            result['data']['msgs'].append(f"do {action} for {action_id}")
        case "load_homes":
            result['data']['msgs'].append(f"do {action} for {action_id}")
            if 1 != UserSettings.objects.filter(pk=action_id).count():
                result['success'] = False
                result['data']['msgs'].append(f"bad settings")
                return JsonResponse(result)

            user_settings = UserSettings.objects.filter(pk=action_id).values()[0]

            try:
                tcc = tuyacloud.TuyaCloudClientNicer(
                    ACCESS_ID=user_settings['access_id'],
                    ACCESS_SECRET=user_settings['access_secret'],
                    UID=user_settings['uid'],
                    ENDPOINT_URL=user_settings['endpoint_url']
                )
            except KeyError:
                result['success'] = False
                result['data']['msgs'].append(f"bad tuyacloud settings")
                return JsonResponse(result)

            homes = tcc.get_user_homes()
            cols = [f.name for f in TuyaHomes._meta.fields]

            for home in homes:
                row = {k: home[k] for k in cols if k in home}
                row['home_id'] = int(row['home_id'])
                row['payload'] = str(home)

                if TuyaHomes.objects.filter(user=action_id, home_id=home["home_id"]).exists():
                    TuyaHomes.objects.filter(user=action_id, home_id=home["home_id"]).update(**row)
                    result['data']['msgs'].append(f'record {action_id}.{home["home_id"]} updated')
                else:
                    obj = TuyaHomes.objects.create(**row)
                    obj.user.add(action_id)
                    result['data']['msgs'].append(f'record {action_id}.{home["home_id"]} added')

        case "load_rooms":
            result['data']['msgs'].append(f"do {action} for {action_id}")
        case "reload_devices":
            result['data']['msgs'].append(f"do {action} for {action_id}")
        case "load_room_devices":
            result['data']['msgs'].append(f"do {action} for {action_id}")
        case "load_all_devices":
            result['data']['msgs'].append(f"do {action} for {action_id}")
            result['data']['msgs'].append('if there\'re empty room devices?')
        case _:
            result['success'] = False
            result['data']['msgs'].append(f"unknown action: {action} for {action_id}")
    return JsonResponse(result)


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

        tcc = tuyacloud.TuyaCloudClientNicer(
            ACCESS_ID="4fuehnegqrfqspnpymn9",
            ACCESS_SECRET="5bb653adee024441aa74fc49f50b6727",
            UID="eu1573240497078AokHW",
            ENDPOINT_URL="openapi.tuyaeu.com"
        )
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
    logger_file_handler = logging.FileHandler(f'{__name__}.log')
    # logger_file_handler.setLevel(logging.DEBUG)
    logger_file_handler.setFormatter(logger_formatter)
    logger1 = logging.getLogger(__name__)
    logger1.setLevel(logging.DEBUG)
    logger1.addHandler(logger_file_handler)
    # logger.info(f"{__file__} updated")
    logger_tuya_cloud_client = logging.getLogger('tuyacloud.TuyaCloudClient')
    logger_tuya_cloud_client.setLevel(logging.DEBUG)
    logger_tuya_cloud_client.addHandler(logger_file_handler)
    return logger1


logger = set_logger()
