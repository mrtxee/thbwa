from django.urls import include, path
from rest_framework import routers

from . import views
from .auth import auth_views as auth
from .devices import devices_views as devices
from .homes import homes_views as homes

router = routers.DefaultRouter()
'''todo:+backend/auth viewsets collection
+POST/api/v2.0/auth/login/google    # return token
+POST/api/v2.0/auth/login           # basic login; return token
+GET /api/v2.0/auth/login           # return user_login_data by token
+GET /api/v2.0/auth/logout/all      # remove token; exit on all_devices
+POST/api/v2.0/auth/register        # register; return token
+POST/api/v2.0/auth/uniquecheck     # is username uniqu check; return bool
+POST/api/v2.0/auth/newpass         # new password set
+POST/api/v2.0/auth/resetpass       # send pw recovery email
+GET /api/v2.0/user                 # return user_data by token
+POST/api/v2.0/user                 # update user_data by token
+GET /api/v2.0/user/settings        # return user_settings by token
+POST/api/v2.0/user/settings        # update user_sett by token
 '''
router.register(r'auth/login/google', auth.LoginGoogleViewSet, 'LoginGoogleViewSet'),
router.register(r'auth/logout/all', auth.LogoutEverywhereViewSet, 'LogoutEverywhereViewSet'),
router.register(r'auth/register', auth.RegisterViewSet, 'RegisterViewSet'),
router.register(r'auth/uniquecheck', auth.UniqueUserNameCheckerViewSet, 'UniqueUserNameCheckerViewSet'),
router.register(r'auth/resetpass', auth.ResetPasswordViewSet, 'ResetPasswordViewSet'),
router.register(r'auth/login', auth.LoginViewSet, 'LoginViewSet'),
router.register(r'user/settings', auth.UserSettingsViewSet, 'UserSettingsViewSet'),
router.register(r'user', auth.UserViewSet, 'UserViewSet'),
router.register(r'user/newpass', auth.NewPasswordViewSet, 'NewPasswordViewSet'),
'''
todo:
 backend/homes
 PUT /api/v2.0/homes/update      /load_homes
+GET /api/v2.0/homes             /get_devices
 backend/devices
+GET /api/v2.0/devices/<str:DEVICE_UUID>/status      /get_device_status/<str:DEVICE_UUID>
+PUT /api/v2.0/devices/<str:DEVICE_UUID>/status      /set_device_status/<str:DEVICE_UUID>

 GET /api/v2.0/devices/<str:DEVICE_UUID>/functions   /get_device_functions/<str:DEVICE_UUID>
 PUT /api/v2.0/devices/<str:DEVICE_UUID>/send_rcc{/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>}  
     -> /send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>
 PUT /api/v2.0/devices/update                        /load_devices
 PUT /api/v2.0/devices/functions/update              /load_device_functions
 PUT /api/v2.0/devices/remotes/update                /load_remotes
 backend/rooms
 PUT /api/v2.0/rooms/update                             /load_rooms
 PUT /api/v2.0/rooms/devices/update                     /set_device_rooms
'''
router.register(r'homes', homes.HomesViewSet, 'HomesViewSet'),
router.register(r'devices/(?P<device_uuid>.*)/status', devices.DevicesViewSet, 'DevicesViewSet'),

# dev test stuff
router.register(r'test403', auth.Test403ResponseViewSet, 'TestResponseViewSet'),
router.register(r'users', views.UserViewSet, 'UserSettingsViewSet')
router.register(r'tuya_homes', views.TuyaHomesViewSet, 'TuyaHomesViewSet'),
urlpatterns = [
    path('', include(router.urls)),
    path('rest/', include('rest_framework.urls', namespace='rest_framework')),
]
'''
//////
del_homes               -> 0
get_context             -> 0
'''
