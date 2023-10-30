import threading

from core.bot_mvc import BotController
from controllers.program_state_controller import ProgramStateControllerSingleton
from controllers.function_executor import FunctionExecutor
from news_handling.news_manager import NewsManager


class ApplicationController:
    def __init__(self):
        self.program_state_controller = ProgramStateControllerSingleton()
        self.condition_lock = self.program_state_controller.get_condition()
        self.news_manager = NewsManager(self.condition_lock, self.program_state_controller)
        self.bot_controller = BotController(self.news_manager, self.condition_lock, self.program_state_controller)
        self.function_executor = FunctionExecutor(3)
        self.start_thread = None
        self.stop_thread = None

    def __run_tasks(self, download_news_delay):
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_controller, download_news_delay,)),
            (self.news_manager.get_world_news, (self.bot_controller, download_news_delay,)),
            (self.bot_controller.start_bot, (self.bot_controller,)),
            (self.bot_controller.stop_bot, (self.bot_controller,)),
        )

    def __stop_tasks(self):
        lock = self.program_state_controller.get_condition()
        with lock:
            self.program_state_controller.set_state(False)
            self.program_state_controller.notify()

    def start(self, download_news_delay: int = 120):
        self.program_state_controller.set_state(True)
        self.start_thread = threading.Thread(target=self.__run_tasks, args=(download_news_delay,))
        self.stop_thread = threading.Thread(target=self.__stop_tasks)
        self.start_thread.start()

    def stop(self):
        self.stop_thread.start()
        self.stop_thread.join()
        self.start_thread.join()
        # print("End of the stop() method in Application class")
