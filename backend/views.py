from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User, Group

from backend.serializers import UserSerializer, GroupSerializer, TuyaHomesSerializer
from main.models import TuyaHomes


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class TuyaHomesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = TuyaHomes.objects.all()
    serializer_class = TuyaHomesSerializer
    permission_classes = [permissions.IsAuthenticated]

# class TuyaHomesList(generics.ListAPIView):
#     serializer_class = TuyaHomesSerializer
#     def get_queryset(self):
#         """
#         This view should return a list of all the purchases
#         for the currently authenticated user.
#         """
#         request = self.request
#         return TuyaHomes.objects.filter(user=request.user.id).values('home_id', 'name', 'geo_name')