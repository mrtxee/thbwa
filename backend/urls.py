from django.urls import include, path
from rest_framework import routers

from . import views
from .auth import auth_views as auth

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, 'UserViewSet')
router.register(r'tuya_homes', views.TuyaHomesViewSet, 'TuyaHomesViewSet'),

router.register(r'homes', views.HomesViewSet, 'HomesViewSet'),
router.register(r'auth/login/google', auth.LoginGoogleViewSet, 'LoginGoogleViewSet'),
router.register(r'auth/login', auth.LoginViewSet, 'LoginViewSet'),
router.register(r'auth/logout/all', auth.LogoutEverywhereViewSet, 'LogoutEverywhereViewSet'),
router.register(r'auth/register', auth.RegisterViewSet, 'RegisterViewSet'),
router.register(r'auth/uniquecheck', auth.UniqueUserNameCheckerViewSet, 'UniqueUserNameCheckerViewSet'),
router.register(r'auth/newpass', auth.NewPasswordViewSet, 'NewPasswordViewSet'),
router.register(r'auth/resetpass', auth.ResetPasswordViewSet, 'ResetPasswordViewSet'),

router.register(r'test403', auth.Test403ResponseViewSet, 'TestResponseViewSet'),
''' todo: backend/auth viewsets collection
+POST/api/v2.0/auth/login/google    # return token
+POST/api/v2.0/auth/login           # basic login; return token
+GET /api/v2.0/auth/login           # return userdata by token
+GET /api/v2.0/auth/logout/all      # remove token; exit on all_devices
+POST/api/v2.0/auth/register        # register; return token
+POST/api/v2.0/auth/uniquecheck     # uniquecheck; return bool
 POST/api/v2.0/auth/newpass         # new password
 POST/api/v2.0/auth/resetpass       # send mail for new pw if token is ok



'''

urlpatterns = [
    path('', include(router.urls)),
    path('rest/', include('rest_framework.urls', namespace='rest_framework')),
]
'''
todo:
backend/devices
GET /api/v2.0/devices/<str:DEVICE_UUID>/status
GET /api/v2.0/devices/<str:DEVICE_UUID>/functions //get_device_functions
PUT /api/v2.0/devices/<str:DEVICE_UUID>/status
PUT /api/v2.0/devices/<str:DEVICE_UUID>/send_rcc {}
PUT /api/v2.0/devices/update
PUT /api/v2.0/devices/functions/update
PUT /api/v2.0/devices/remotes/update

backend/homes
PUT /api/v2.0/homes/update
GET /api/v2.0/homes

backend/rooms
PUT /api/v2.0/rooms/update
PUT /api/v2.0/rooms/devices/update


//////


/get_devices                             ->+GET /api/v2.0/homes
/get_device_status/<str:DEVICE_UUID>     -> GET /api/v2.0/devices/<str:DEVICE_UUID>/status
/set_device_status/<str:DEVICE_UUID>     -> POST/api/v2.0/devices/<str:DEVICE_UUID>/status
/get_device_functions/<str:DEVICE_UUID>  -> GET /api/v2.0/devices/<str:DEVICE_UUID>/functions
/send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>
                                          -> POST /api/v2.0/devices/<str:DEVICE_UUID>/send_rcc
                                             {/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>}
load_homes              -> PUT /api/v2.0/homes/update 
load_rooms              -> PUT /api/v2.0/rooms/update
load_devices            -> PUT /api/v2.0/devices/update
set_device_rooms        -> PUT /api/v2.0/rooms/devices/update
load_device_functions   -> PUT /devices/functions/update
load_remotes            -> PUT /devices/remotes/update
del_homes               -> 0
get_context             -> 0
'''
