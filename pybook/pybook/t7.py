import threading


class SingletonMetaClass(type):
    instances = {}
    lock = threading.Lock()

    def __call__(cls, *args, **kwds):
        with cls.lock:
            if cls not in cls.instances:
                cls.instances[cls] = super().__call__(*args, **kwds)
        return cls.instances[cls]


class DatabaseConnection:
    def __init__(self, user, pwd):
        self.user = user
        self.password = pwd

    def connect_str(self):
        return self.user + ":" + self.password


class DatabaseConnectionSingleton(metaclass=SingletonMetaClass):
    def __init__(self, user, pwd):
        self.user = user
        self.password = pwd

    def connect_str(self):
        return self.user + ":" + self.password
