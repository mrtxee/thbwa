from django.db import models
from django.conf import settings
from django.forms import ModelForm


class TuyaHomes(models.Model):
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)
    home_id = models.PositiveIntegerField(primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=255, null=True)
    geo_name = models.CharField(max_length=255, null=True)
    payload = models.JSONField()


class TuyaRooms(models.Model):
    pass


class TuyaDevices(models.Model):
    pass


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
