"""thbwa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from main import views
from thbwa import settings

urlpatterns = [
    path('', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('user/profile/', views.user_profile, name='profile'),
    path('devices/', views.devices, name='devices'),
    path('api/', include('main.urls'), name='api'),
    path('boo/<str:ACTION>', views.boo, name='boo'), # специальные методы с БД
    path('accounts/', include('allauth.urls'), name='accounts'),
    path('admin/', admin.site.urls, name='admin'),
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico', permanent=True)),

    #re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]


