import threading

from core.bot_mvc import BotController
from controllers.program_state_controller import ProgramStateControllerSingleton
from controllers.function_executor import FunctionExecutor
from news_handling.news_manager import NewsManager
import logging


class ApplicationController:
    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Start of the __init__() method in ApplicationController class")
        self.program_state_controller = ProgramStateControllerSingleton()
        self.condition_lock = self.program_state_controller.get_condition()
        self.function_executor = FunctionExecutor(max_workers=3, logger=self.logger)
        self.news_manager = NewsManager(self.condition_lock, self.program_state_controller, self.logger)
        self.bot_controller = BotController(self.news_manager, self.condition_lock, self.program_state_controller)
        self.start_thread = None
        self.stop_thread = None
        self.logger.debug("End of the __init__() method in ApplicationController class")

    def __run_tasks(self, download_news_delay):
        self.logger.debug("Start of the __run_tasks() method in ApplicationController class")
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_controller, download_news_delay,)),
            (self.news_manager.get_world_news, (self.bot_controller, download_news_delay,)),
            (self.bot_controller.start_bot, (self.bot_controller,)),
            (self.bot_controller.stop_bot, (self.bot_controller,)),
        )
        self.logger.debug("End of the __run_tasks() method in ApplicationController class")

    def __stop_tasks(self):
        self.logger.debug("Start of the __stop_tasks() method in ApplicationController class")
        lock = self.program_state_controller.get_condition()
        with lock:
            self.program_state_controller.set_state(False)
            self.program_state_controller.notify()
        self.logger.debug("End of the __stop_tasks() method in ApplicationController class")

    def start(self, download_news_delay: int = 120):
        self.logger.debug("Start of the start() method in Application class")
        self.program_state_controller.set_state(True)
        self.start_thread = threading.Thread(target=self.__run_tasks, args=(download_news_delay,))
        self.stop_thread = threading.Thread(target=self.__stop_tasks)
        self.start_thread.start()
        self.logger.debug("End of the start() method in Application class")

    def stop(self):
        self.logger.debug("Start of the stop() method in Application class")
        self.stop_thread.start()
        self.stop_thread.join()
        self.start_thread.join()
        self.logger.debug("End of the stop() method in Application class")
