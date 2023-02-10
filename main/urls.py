from django.urls import path, re_path

from . import views

urlpatterns = [
    path('v1.0/<str:ACTION>', views.api, name='api'),
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