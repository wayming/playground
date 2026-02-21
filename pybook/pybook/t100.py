import threading


class t100_Counter_MT:
    def __init__(self):
        self.global_counter = 0
        self.lock = threading.Lock()
        self.local_counter = threading.local()
        self.local_counter.value = 0
        pass

    def increase(self, v):
        self.local_counter.value = v
        with self.lock:
            self.global_counter += v

    def print_local(self):
        print(self.local_counter.value)

    def print(self):
        print("local ", self.local_counter.value)
        print("global ", self.global_counter)
