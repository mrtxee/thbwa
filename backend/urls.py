from django.urls import include, path, re_path
from django.http import HttpResponse
from rest_framework import routers
from . import views
from .views import MyRESTView
from django.contrib.auth.decorators import login_required

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'UserViewSet')
router.register(r'groups', views.GroupViewSet, 'GroupViewSet')
router.register(r'homes', views.TuyaHomesViewSet, 'TuyaHomesViewSet')
#router.register(r'my-model/', views.YourView, basename='MyModel')
#router.register(r'YourView', views.YourView, 'YourView')

urlpatterns = [
    path('', include(router.urls)),
    path('del_homes/', lambda request: HttpResponse('del_homes'), name='del_homes'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),

    re_path(r'^myview[/]?$', login_required(MyRESTView.as_view()), name='myview'),

]

'''
del_homes
load_homes
load_rooms
load_devices
set_device_rooms
get_devices
get_context
load_remotes
load_device_functions
    path('v1.0/send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>', views.api_send_rcc, name='get_device_status'),
    path('v1.0/get_device_status/<str:DEVICE_UUID>', views.api_get_device_status, name='get_device_status'),
    path('v1.0/set_device_status/<str:DEVICE_UUID>', views.api_set_device_status, name='set_device_status'),
    path('v1.0/get_device_functions/<str:DEVICE_UUID>', views.api_get_device_functions, name='api_get_device_functions'),
'''