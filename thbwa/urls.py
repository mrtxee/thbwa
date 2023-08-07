from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from main import views
from thbwa import settings

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('user/profile/', views.user_profile, name='profile'),
    path('devices/', views.devices, name='devices'),
    path('boo/<str:ACTION>', views.boo, name='boo'),  # специальные методы с БД
    path('accounts/', include('allauth.urls'), name='accounts'),
    path('admin/', admin.site.urls, name='admin'),

    path('api/v2.0/', include('backend.urls'), name='api20'),
    path('api/v1.0/', include('main.urls'), name='api10'),

    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]
