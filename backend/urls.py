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
router.register(r'auth/register', auth.RegisterViewSet, 'RegisterViewSet'),
router.register(r'auth/uniquecheck', auth.UniqueUserNameCheckerViewSet, 'UniqueUserNameCheckerViewSet'),
router.register(r'auth/newpassword', auth.NewPasswordViewSet, 'NewPasswordViewSet'),

router.register(r'test403', auth.Test403ResponseViewSet, 'TestResponseViewSet'),
''' todo:
backend/auth
+POST/api/v2.0/auth/login/google    # return token
+POST/api/v2.0/auth/login           # basic login; return token
+GET /api/v2.0/auth/login           # return userdata by token
 POST/api/v2.0/auth/register        # register; return token
 POST/api/v2.0/auth/uniquecheck     # uniquecheck; return token
 POST/api/v2.0/auth/newpassword     # newpassword; return token


 GET /api/v2.0/auth/logout          # remove token; return removal status


'''

urlpatterns = [
    path('', include(router.urls)),
    path('rest/', include('rest_framework.urls', namespace='rest_framework')),
    # path("dj-rest-auth/google/login/", GoogleLoginView.as_view(), name="google_login"
    # path('rest/google', GoogleLogin.as_view(), name='google_login'),
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
