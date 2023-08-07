from django.urls import path

from . import views

urlpatterns = [
    path('v1.0/<str:ACTION>', views.api, name='api'),
    path(
        'v1.0/send_rcc/<str:DEVICE_UUID>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>',
        views.api_send_rcc, name='get_device_status'),
    path('v1.0/get_device_status/<str:DEVICE_UUID>', views.api_get_device_status, name='get_device_status'),
    path('v1.0/set_device_status/<str:DEVICE_UUID>', views.api_set_device_status, name='set_device_status'),
    path('v1.0/get_device_functions/<str:DEVICE_UUID>', views.api_get_device_functions,
         name='api_get_device_functions'),
]
