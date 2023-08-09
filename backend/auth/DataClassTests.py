from dataclasses import dataclass, asdict


@dataclass
class Userdata:
    username: str = ''
    picture: str = ''
    name: str = ''
    email: str = ''
    token: str = ''

    def dict(self):
        if not self.username or self.name or self.email:
            raise ValueError()
        return asdict(self)


u = Userdata(username='vasya', picture='vasya', name='Вася', email='email')
print( u )
u.name='petya'
print( u.dict() )

u1 = Userdata(username='vasya')
print( u1.dict() )

u2 = Userdata()
print( u2.dict() )
