import threading
import time

from news_handling.news_scraper import NewsScraper
from core.bot_mvc import BotController
from news_handling.news_storage import NewsStorage


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller, logger):
        self.scraper = NewsScraper(logger)
        self.lock = condition_lock
        self.program_state_controller = program_state_controller
        self.logger = logger
        self.news_storage = NewsStorage(logger)

    def get_world_news(self, a_bot_controller: BotController, delay: int = 60):
        get_program_state = self.program_state_controller.is_program_running
        while get_program_state():
            with self.lock:
                self.logger.debug("In task get_world_news")
                a_bot_controller.bot_model.world_news_dict = self.scraper.get_world_news()
                # If there are no files world_news.json and world_news_timestamp.txt, get the world news and timestamp
                # from the scraper and store them in world_news.json and world_news_timestamp.json respectively.

                # Else, get world news from the storage.
                # Check if the difference between current time and world_news_timestamp.json is more than "delay"
                # seconds then get news from the scraper
                self.logger.debug(f"Count of World news: {len(a_bot_controller.bot_model.world_news_dict)}")
                self.logger.debug(f"Sleeping in get_world_news on {delay}...")
                self.lock.notify_all()
                t0 = time.time()
                self.__waiting_for_finish_the_program_or_timeout(delay, t0)
        self.logger.debug("End of task get_world_news")

    def get_ua_news(self, a_bot_controller: BotController, delay: int = 60):
        get_program_state = self.program_state_controller.is_program_running
        while get_program_state():
            with self.lock:
                self.logger.debug("In task get_ua_news")
                a_bot_controller.bot_model.ua_news_dict = self.scraper.get_ua_news()
                self.logger.debug(f"Count of UA news: {len(a_bot_controller.bot_model.ua_news_dict)}")
                self.logger.debug(f"Sleeping in get_ua_news on {delay}...")
                self.lock.notify_all()
                t0 = time.time()
                self.__waiting_for_finish_the_program_or_timeout(delay, t0)
        self.logger.debug("End of task get_ua_news")

    def __waiting_for_finish_the_program_or_timeout(self, delay, t0):
        while self.program_state_controller.is_program_running() and time.time() - t0 < delay:
            self.lock.wait(delay)

    def get_news(self, a_bot_controller: BotController, delay: int = 60):
        get_program_state = self.program_state_controller.is_program_running
        while get_program_state():
            with self.lock:
                self.logger.debug("In task get_world_news")
                a_bot_controller.bot_model.world_news_dict = self.scraper.get_news()
                # If there are no files world_news.json and world_news_timestamp.txt, get the world news and timestamp
                # from the scraper and store them in world_news.json and world_news_timestamp.json respectively.

                # Else, get world news from the storage.
                # Check if the difference between current time and world_news_timestamp.json is more than "delay"
                # seconds then get news from the scraper
                self.logger.debug(f"Count of NEWS news: {len(a_bot_controller.bot_model.world_news_dict)}")
                self.logger.debug(f"Sleeping in get_world_news on {delay}...")
                self.lock.notify_all()
                t0 = time.time()
                self.__waiting_for_finish_the_program_or_timeout(delay, t0)
        self.logger.debug("End of task get_world_news")
