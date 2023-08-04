from django.contrib.auth.models import User, Group
from backend.serializers import UserSerializer, GroupSerializer, TuyaHomesSerializer, YourSerializer
from main.models import TuyaHomes

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

class MyRESTView(APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        # see https://stackoverflow.com/questions/13603027/django-rest-framework-non-model-serializer?rq=3
        get_arg1 = request.GET.get('arg1', 'def')
        get_arg2 = request.GET.get('arg2', 0)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)
        #result = myClass.do_work()
        result = get_arg1
        response = Response(result, status=status.HTTP_200_OK)
        return response

class UserViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class TuyaHomesViewSet(viewsets.ReadOnlyModelViewSet):
    """ API endpoint that allows groups to be viewed or edited.
        Filtered over the current user
    """
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
