from django.contrib.auth.models import User
from rest_framework import serializers

from main.models import TuyaHomes

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class TuyaHomesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TuyaHomes
        fields = ['home_id', 'name', 'geo_name']

# class YourSerializer(serializers.Serializer):
#    """Your data serializer, define your fields here."""
#    comments = serializers.IntegerField()
#    likes = serializers.IntegerField()