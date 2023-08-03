from django.urls import include, path, re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'homes', views.TuyaHomesViewSet)

urlpatterns = [
    #DJANGO RESTAPI EX
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),

    #re_path(r'v1.0/*', views.api, name='api'),
]

'''
MODEL
device
home
...

dispatcher ->
    controller.devices() <- SINGLETON 
        var device = deviceService.getDevices()
            {var tuyaFormattedDiveces = tuyaClien.getDevice()
            var device = deviceMapper.fromTuyaFormat(tuyaFormattedDiveces)
            return device}
        //return deviceMapper.toJson(device);
        //return this.toResponse(...)   
    controller.api_load_homes()
        -> homeService.updateHomes()
    controller.api_load_rooms()    
    
    in controller we have method toResponse(device, success: boolean, ....) {
        var  json = {}
        json.success = ture
        ....
        json.payload = deviceMapper.toJson(device); 
         
    }
'''