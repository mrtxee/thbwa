from django.conf import settings
from django.db import models
from django.forms import ModelForm


class TuyaHomes(models.Model):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)
    home_id = models.PositiveIntegerField(primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=255, null=True)
    geo_name = models.CharField(max_length=255, null=True)
    payload = models.JSONField()


class TuyaHomeRooms(models.Model):
    home = models.ForeignKey(TuyaHomes, on_delete=models.CASCADE, null=False, unique=False)
    room_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    payload = models.JSONField()


class TuyaDeviceFunctions(models.Model):
    product_id = models.CharField(max_length=255, primary_key=True)
    category = models.CharField(max_length=255)
    functions = models.JSONField(default=None, null=True)
    status = models.JSONField(default=None, null=True)
    payload = models.JSONField()


class TuyaDevices(models.Model):
    uuid = models.CharField(max_length=64, primary_key=True)
    room = models.ForeignKey(TuyaHomeRooms, on_delete=models.CASCADE, null=True, unique=False, default=None)
    home = models.ForeignKey(TuyaHomes, on_delete=models.CASCADE, null=False, unique=False)
    owner_id = models.PositiveIntegerField(null=False)
    device_id = models.CharField(max_length=64, default=None, null=False)
    name = models.CharField(max_length=255, null=False)
    icon_url = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255, null=False)
    product_name = models.CharField(max_length=255, null=False)
    local_key = models.CharField(max_length=255, null=False)
    payload = models.JSONField()


class TuyaDeviceRemotekeys(models.Model):
    device = models.OneToOneField(TuyaDevices, primary_key=True, on_delete=models.CASCADE)
    parent_id = models.CharField(max_length=64, default=None, null=False)
    remote_index = models.PositiveIntegerField(unique=False, null=False)
    category_id = models.PositiveIntegerField(unique=False, null=False)
    key_list = models.JSONField()
    payload = models.JSONField()


TUYA_CLOUD_ENDPOINTS = (
    ('openapi.tuyaus.com', 'America'),
    ('openapi.tuyacn.com', 'China'),
    ('openapi.tuyaeu.com', 'Europe'),
    ('openapi.tuyain.com', 'India'),
    ('openapi-ueaz.tuyaus.com', 'EasternAmerica'),
    ('openapi-weaz.tuyaeu.com', 'WesternEurope'),
)


class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    access_id = models.CharField(max_length=40)
    access_secret = models.CharField(max_length=40)
    uid = models.CharField(max_length=40)
    endpoint_url = models.CharField(max_length=23, choices=TUYA_CLOUD_ENDPOINTS)


class UserSettingsForm(ModelForm):
    class Meta:
        model = UserSettings
        # access_id = forms.DateField(required=False)
        fields = ['access_id', 'access_secret', 'uid', 'endpoint_url']
