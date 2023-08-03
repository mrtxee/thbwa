from django.contrib.auth.models import User, Group
from rest_framework import serializers

from main.models import TuyaHomes


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class TuyaHomesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TuyaHomes
        fields = ['home_id', 'name', 'geo_name']

class YourSerializer(serializers.Serializer):
   """Your data serializer, define your fields here."""
   comments = serializers.IntegerField()
   likes = serializers.IntegerField()