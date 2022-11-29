# thbwa
 TuyaHomeBot Web Application

## RestApi
методы, которые перекачивают данные из tuya в l_db:

    GET: /api/v1.0/load_homes/<UID>
    #PATCH: /api/v1.0/homes + с авторизацией
    /api/v1.0/load_rooms/<UID>
    /api/v1.0/load_devices/<UID>
    /api/v1.0/set_device_rooms/<UID>
методы, которые передают данные во фронтэнд:

    GET: /api/v1.0/get_devices/<UID>
    #GET: /api/v1.0/devices + с авторизацией
    auth2

'''
    #todo : потом когда-нибудь сделать авторизацию
    авторизацию вместо UID
'''


## Текущие вопросы ХарпСергу:

По Django framework у нас следующая структура:
### ./main/views.py - URL-диспетчер
обрабатывает URL-path, headers, POST, PULL, GET и передает в контроллер (back-end) 
```python
urlpatterns = [
    path('v1.0/<str:ACTION>/<str:action_id>', views.api, name='api'),
    re_path(r'v1.0/*', views.api, name='api'),
]
```
### ./main/views.py - контроллер
#### Вопрос по методу **def api()**.

Метод принимает данные от url-диспетчера и возвращает ответ в форме `JsonResponse(result)`. Он использует SWITCH-CASE, чтобы определить поступившую команду.

Все CASE-ы устроены примерно одинаково
 - проверить, корректность данных
 - создать экземпляр `tcc = tuyacloud.TuyaCloudClientNicer()`
 - через tcc получить данные, изменить БД

При этом на всех этапах работы метода формируется древовидный объект `result`, который в итоге уходит пользователю `return JsonResponse(result)`

Ты говоришь что надо создать сервисный слой с синглетоном и методом api().

Мне трудно выдернуть кусок кода из `api()`, так как он формирует объект result для ответа в рест, но с другой стороны в каждом CASE создавать `tcc = tuyacloud*()` - глупо.

Синглетон - это класс. А все что происходит во `views.py` - это функции, которые вызываются из URL-диспетчера.

Поэтому запрос уточнений к твоему совету: 
 - В каком файле должен быть описан класс Синглетон?
 - Что должен включать синглетон? Он просто должен быть оберткой `TuyaCloudClientNicer()`, которая на уровне конструктора проверяет сущетсвует ли экземпляр и возвращает либо новый, либо ссылку на сщуетсвующий?
 - Надо ли отделить формирование объекта `JsonResponse(result)` от остальной логики и как это сделать? 
