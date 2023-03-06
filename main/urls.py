from django.urls import path, re_path

from . import views

urlpatterns = [
    path('v1.0/<str:ACTION>', views.api, name='api'),
    #DEVICE_UUID=None, REMOTE_UUID=None, CATEGORY_ID=None, REMOTE_INDEX=None, KEY=None, KEY_ID=None):
    path('v1.0/send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>', views.api_send_rcc, name='get_device_status'),
    path('v1.0/get_device_status/<str:DEVICE_UUID>', views.api_get_device_status, name='get_device_status'),
    path('v1.0/set_device_status/<str:DEVICE_UUID>', views.api_set_device_status, name='set_device_status'),
    path('v1.0/get_device_functions/<str:DEVICE_UUID>', views.api_get_device_functions, name='api_get_device_functions'),

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