from django.urls import path, re_path

from . import views

"""
    -/api/v1.0/truncate_devices/<UID:localDB userID>
    -/api/v1.0/reload_devices/<UID>
    /api/v1.0/load_homes/<UID>
    /api/v1.0/load_rooms/<UID>
    /api/v1.0/load_devices/<UID>
    /api/v1.0/set_device_rooms/<UID>
    другие методы рест-апи
    /api/v1.0/get_devices/<UID>
    /api/v1.0/load_device_status/<UID>/<UUID:device Tuya UUID>
    
    ДИСПАТЧЕР_СЕРВЕЛЕТ
    URL-ДИСПЕТЧЕР
"""

urlpatterns = [
    path('v1.0/<str:ACTION>/<str:USER_ID>', views.api, name='api'),
    path('v1.0/load_device_status/<str:USER_ID>/<str:DEVICE_UUID>', views.api_load_device_status, name='api'),
    #path('v1.0/load_homes/<str:USER_ID>', views.api, name='api_load_homes'),
    #path('v1.0/load_rooms/<str:USER_ID>', views.api, name='api_load_rooms'),
    #path('v1.0/get_devices/<str:USER_ID>', controller.devices(), name='api_load_rooms'),
    re_path(r'v1.0/*', views.api, name='api'),
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