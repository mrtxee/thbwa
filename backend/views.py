from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.serializers import UserSerializer, TuyaHomesSerializer
from main.models import TuyaHomes


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated() and request.user.is_admin
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False
    # def has_object_permission(self, request, view, obj):
    #     # Deny actions on objects if the user is not authenticated
    #     if not request.user.is_authenticated():
    #         return False
    #     if view.action == 'retrieve':
    #         return obj == request.user or request.user.is_admin
    #     elif view.action in ['update', 'partial_update']:
    #         return obj == request.user or request.user.is_admin
    #     elif view.action == 'destroy':
    #         return request.user.is_admin
    #     else:
    #         return False


# https://django.fun/ru/docs/django-rest-framework/3.12/api-guide/authentication/

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class TuyaHomesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TuyaHomesSerializer
    queryset = TuyaHomes.objects.all().order_by('home_id')

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user.id).values('home_id', 'name', 'geo_name')
        return query_set


""" todo: API endpoint to perform some action.
    Filtered over the current user
"""

""" todo: API endpoint to read-only result.
    Filtered over the current user
"""


class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
