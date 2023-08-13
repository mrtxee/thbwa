from django.urls import include, path
from rest_framework import routers

from . import views
from .auth import auth_views as auth
from .devices import devices_views as devices
from .homes import homes_views as homes
from .rooms import rooms_views as rooms

router = routers.DefaultRouter()
'''todo:
 backend/auth
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
 backend/homes
+PUT /api/v2.0/homes/load
+GET /api/v2.0/homes
 backend/devices
+GET /api/v2.0/devices/<str:device_uuid>/status    
+PUT /api/v2.0/devices/<str:device_uuid>/status    
+PUT /api/v2.0/devices/<str:device_uuid>/rcc       
+PUT /api/v2.0/devices/load                        
+PUT /api/v2.0/devices/functions/load              
+PUT /api/v2.0/devices/remotes/load                
 backend/rooms
+PUT /api/v2.0/rooms/load                          
+PUT /api/v2.0/rooms/devices/load            
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
router.register(r'homes', homes.HomesViewSet, 'HomesViewSet'),
router.register(r'homes/load', homes.HomesLoadViewSet, 'HomesLoadViewSet'),
router.register(r'devices/load', devices.DevicesLoadViewSet, 'DevicesLoadViewSet'),
router.register(r'devices/functions/load', devices.DevicesFunctionsLoadViewSet, 'DevicesFunctionsLoadViewSet'),
router.register(r'devices/remotes/load', devices.DevicesRemotesLoadViewSet, 'HomesLoadViewSet4'),
router.register(r'devices/(?P<device_uuid>.*)/(?P<cmd>.*)', devices.DevicesViewSet, 'DevicesViewSet'),
router.register(r'rooms/load', rooms.RoomsLoadViewSet, 'RoomsLoadViewSet'),
router.register(r'rooms/devices/load', rooms.RoomsDevicesLoadViewSet, 'RoomsDevicesLoadViewSet'),

urlpatterns = [
    path('', include(router.urls)),
    path('rest/', include('rest_framework.urls', namespace='rest_framework')),
]
