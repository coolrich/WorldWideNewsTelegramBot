import concurrent.futures
import threading
import time

from news_manager import NewsManager
from bot_mvc import BotController


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

    def get_state(self):
        return self.__is_running

    def set_state(self, state):
        self.__is_running = state

    def get_condition(self):
        return self.condition

    def notify(self):
        self.condition.notify_all()


class FunctionExecutor:
    def __init__(self, max_workers):
        self.max_workers = max_workers
        # self.interval = interval

    def execute_functions_periodically(self, *functions_with_args):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for func, args in functions_with_args:
                print("function:", func, "args:", args)
                if args is not None:
                    futures.append(executor.submit(func, *args))
                else:
                    futures.append(executor.submit(func))
            # concurrent.futures.wait(futures)
            print("End of the execute_functions_periodically() method in FunctionExecutor class")


class Application:
    def __init__(self):
        self.program_state_controller = ProgramStateControllerSingleton()
        self.condition_lock = self.program_state_controller.get_condition()
        self.news_manager = NewsManager(self.condition_lock, self.program_state_controller)
        self.bot_controller = BotController(self.news_manager, self.condition_lock, self.program_state_controller)
        self.function_executor = FunctionExecutor(3)

    def start(self, download_news_delay: int = 120):
        self.__run_tasks(download_news_delay)

    def __run_tasks(self, download_news_delay):
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_controller, download_news_delay,)),
            (self.news_manager.get_world_news, (self.bot_controller, download_news_delay,)),
            (self.bot_controller.start_bot, (self.bot_controller,)),
            (self.bot_controller.stop_bot, (self.bot_controller,)),
        )

    def stop(self):
        lock = self.program_state_controller.get_condition()
        with lock:
            self.program_state_controller.set_state(False)
            self.program_state_controller.notify()
        print("End of the stop() method in Application class")


class ApplicationController:
    def __init__(self):
        self.app = Application()
        self.start_thread = None
        self.stop_thread = None

    def start(self):
        self.start_thread = threading.Thread(target=self.app.start)
        self.stop_thread = threading.Thread(target=self.app.stop)
        self.start_thread.start()

    def stop(self):
        self.stop_thread.start()
        self.stop_thread.join()
        self.start_thread.join()


# Test
if __name__ == "__main__":
    app_controller = ApplicationController()
    app_controller.start()
    time.sleep(10)
    print("Start program shutdown...")
    app_controller.stop()
    print("The program has been finished.")
