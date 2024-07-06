# thbwa ~ tho
https://tuyahome.online/

## деплой на локальном стенде
    # скачать сурсы, перейти в папку
    cd c:\PycharmProjects\thbwa\
    python -m venv .venv
    
    # powershell case
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    .venv\Scripts\Activate.ps1
    
    python -m pip install --upgrade pip
    pip install django==4.2.4
    pip install django-allauth==0.54.0
    pip install django_bootstrap5==23.3
    pip install django-cors-headers==4.2.0
    pip install python-dotenv==1.0.0
    pip install djangorestframework==3.14.0
    pip install dacite==1.8.1
    python manage.py runserver
    
    deactivate # -- выйти из venv

## настройки приложения
- .env
- thbwa/settings.py