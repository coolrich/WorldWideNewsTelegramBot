import threading


class ProgramStateControllerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "__is_running"):
            self.__is_running = True
            self.condition = threading.Condition()
            self.rlock = threading.RLock()

    def get_state(self):
        return self.__is_running

    def set_state(self, state):
        self.__is_running = state

    def get_condition(self):
        return self.condition

    def notify(self):
        self.condition.notify_all()
