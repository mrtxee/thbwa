from django.urls import path

from . import views

urlpatterns = [
    path('<str:ACTION>', views.api, name='api101'),
    path(
        'send_rcc/<str:DEVICE_UUID>/<str:remote_uuid>/<str:CATEGORY_ID>/<str:REMOTE_INDEX>/<str:KEY>/<str:KEY_ID>',
        views.api_send_rcc, name='get_device_status'),
    path('get_device_status/<str:DEVICE_UUID>', views.api_get_device_status, name='get_device_status'),
    path('set_device_status/<str:DEVICE_UUID>', views.api_set_device_status, name='set_device_status'),
    path('get_device_functions/<str:DEVICE_UUID>', views.api_get_device_functions,
         name='api_get_device_functions'),
]
