from django.urls import path, re_path

from . import views

"""
    /api/v1.0/truncate_devices/<UID>
    /api/v1.0/reload_devices/<UID>
    /api/v1.0/load_homes/<UID>
    /api/v1.0/load_rooms/<home_id>
    /api/v1.0/load_room_devices/<room_id>
    /api/v1.0/load_all_devices/<UID>
    другие методы рест-апи
    /api/v1.0/get_devices/<UID>

"""

urlpatterns = [
    path('v1.0/<str:ACTION>/<str:USER_ID>', views.api, name='api'),
    re_path(r'v1.0/*', views.api, name='api'),
]
