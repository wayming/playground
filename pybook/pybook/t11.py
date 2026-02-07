class User:
    def __init__(self, user, pwd, age):
        self.user = user
        self.password = pwd
        self.age = age

    @property
    def user(self):
        return self._user_name

    @user.setter
    def user(self, user: str):
        if not user.isascii():
            raise ValueError("user name must be ascii text")
        self._user_name = user

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd: str):
        if pwd.isnumeric():
            raise ValueError("password must contain characters and numbers")
        self._password = pwd

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age: int):
        if age < 0 or age > 100:
            raise ValueError("Invalid age")
        self._age = age
