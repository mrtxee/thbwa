from dataclasses import asdict, dataclass

from dacite import from_dict


@dataclass
class UserLoginData:
    username: str = ''
    name: str = ''
    picture: str = ''
    token: str = ''

    def set_name_by_user(self, user):
        self.name = f"{user.first_name} {user.last_name}".strip() if len(
            f"{user.first_name}{user.last_name}".strip()) > 0 else user.username

    def set_email_by_user(self, user):
        self.email = user.email if len(user.email.strip()) > 0 else f"{user.username}@mailto.plus"

    def dict(self):
        if not self.username or not self.name:
            raise ValueError()
        return asdict(self)


@dataclass
class UserData(UserLoginData):
    last_login: str = ''
    date_joined: str = ''
    last_name: str = ''
    email: str = ''
    first_name: str = ''

    def dict(self):
        if not self.username or not self.name or not self.email:
            raise ValueError()
        return asdict(self)


@dataclass
class UserSettingsData:
    access_id: str = ''
    access_secret: str = ''
    uid: str = ''
    endpoint_url: str = ''

    def dict(self):
        return asdict(self)


json1 = {
    "access_id": "4fuehnegqrfqspnpymn9",

    "uid": "eu1573240497078AokHW",
    "endpoint_url": "openapi.tuyaeu.com"
}

us = UserSettingsData(access_secret='secss');
print(us)
us = from_dict(data_class=UserSettingsData, data=json1)
print(us)

ud = UserData()
print(ud)

ul = UserLoginData(username='username', name='name', token='to')
print(ul)
print(ul.dict())
