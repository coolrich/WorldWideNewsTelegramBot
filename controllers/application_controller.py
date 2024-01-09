import threading

from core.bot_controller import BotController
from controllers.program_state_controller import program_state_controller as psc
from controllers.function_executor import FunctionExecutor
import logging


class ApplicationController:
    def __init__(self, is_debug_mode: bool = False):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s',
            handlers=[
                logging.StreamHandler(),
            ]
        )
        self.logger = logging.getLogger(__name__)

        if not is_debug_mode:
            logging.disable(logging.DEBUG)
        self.logger.debug("Start of the __init__() method in ApplicationController class")
        self.condition_lock = psc.get_condition()
        self.function_executor = FunctionExecutor(max_workers=3, logger=self.logger)
        self.bot_controller = BotController(self.condition_lock, self.logger)
        self.start_thread = None
        self.stop_thread = None
        self.logger.debug("End of the __init__() method in ApplicationController class")

    def __run_tasks(self, download_news_delay):
        self.logger.debug("Start of the __run_tasks() method in ApplicationController class")
        self.function_executor.execute_functions_periodically(
            (self.bot_controller.start_bot, (self.bot_controller,)),
            (self.bot_controller.stop_bot, (self.bot_controller,)),
        )
        self.logger.debug("End of the __run_tasks() method in ApplicationController class")

    def __stop_tasks(self):
        self.logger.debug("Start of the __stop_tasks() method in ApplicationController class")
        lock = psc.get_condition()
        with lock:
            psc.set_state(False)
            psc.notify_all()
        self.logger.debug("End of the __stop_tasks() method in ApplicationController class")

    def start(self, download_news_delay: int = 120):
        self.logger.debug("Start of the start() method in Application class")
        psc.set_state(True)
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
