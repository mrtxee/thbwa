from django.urls import path

from . import views

urlpatterns = [
    path('<str:ACTION>', views.api, name='api101'),
    path(
        'send_rcc/<str:device_uuid>/<str:REMOTE_UUID>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>',
        views.api_send_rcc, name='get_device_status'),
    path('get_device_status/<str:device_uuid>', views.api_get_device_status, name='get_device_status'),
    path('set_device_status/<str:device_uuid>', views.api_set_device_status, name='set_device_status'),
    path('get_device_functions/<str:device_uuid>', views.api_get_device_functions,
         name='api_get_device_functions'),
]
