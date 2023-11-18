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
            self.__is_news_ready = False

    def is_news_ready(self):
        return self.__is_news_ready

    def set_news_state(self, state: bool):
        self.__is_news_ready = state

    def get_program_state(self):
        return self.__is_running

    def set_state(self, state):
        self.__is_running = state

    def get_condition(self):
        return self.condition

    def notify_all(self):
        self.condition.notify_all()


program_state_controller = ProgramStateControllerSingleton()
