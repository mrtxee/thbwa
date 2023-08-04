from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'UserViewSet')
router.register(r'groups', views.GroupViewSet, 'GroupViewSet')
router.register(r'homes', views.HomesViewSet, 'HomesViewSet'),

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
'''
+get_devices                             -> GET /api/v2.0/homes
/get_device_status/<str:DEVICE_UUID>     -> GET /api/v2.0/devices/<str:DEVICE_UUID>/status
/set_device_status/<str:DEVICE_UUID>     -> POST /api/v2.0/devices/<str:DEVICE_UUID>/status
/get_device_functions/<str:DEVICE_UUID>  -> GET /api/v2.0/devices/<str:DEVICE_UUID>/functions
/send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>
                                            -> POST /api/v2.0/devices/<str:DEVICE_UUID>/send_rcc {/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>}
load_homes              -> PUT /homes/update 
load_rooms              -> PUT /rooms/update
load_devices            -> PUT /devices/update
set_device_rooms        -> PUT /devices/rooms/update
load_device_functions   -> PUT /devices/functions/update
load_remotes            -> PUT /devices/remotes/update
del_homes               -> 0
get_context             -> 0
'''

'''
SAMPLES OF urlpatterns
    path('del_homes/', lambda request: HttpResponse('del_homes'), name='del_homes'),
    re_path(r'^myview[/]?$', login_required(MyRESTView.as_view()), name='myview'),
'''