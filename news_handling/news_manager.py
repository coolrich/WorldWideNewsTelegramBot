import threading
import time
from enum import Enum

from news_handling.news_scraper import UANewsScraper, WorldNewsScraper
from core.bot_mvc import BotController
from news_handling.news_storage import NewsStorage
from countries.countries import Countries


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller, logger):
        self.__scrapers = [WorldNewsScraper(logger), UANewsScraper(logger)]
        self.__lock = condition_lock
        self.__program_state_controller = program_state_controller
        self.__is_program_running = self.__program_state_controller.is_program_running
        self.__logger = logger
        self.news_storage = {country: None for country in Countries}

    def get_news(self, a_bot_controller: BotController, delay: int = 60):
        while self.__is_program_running():
            for scraper in self.__scrapers:
                with self.__lock:
                    self.__logger.debug("In task get_world_news")
                    # a_bot_controller.bot_model.world_news_dict = scraper.load_news()
                    a_bot_controller.bot_model.news_dict = scraper.load_news()
                    # If there are no files world_news.json and world_news_timestamp.txt, get the world news and
                    # timestamp from the scraper and store them in world_news.json and world_news_timestamp.json
                    # respectively.

                    # Else, get world news from the storage.
                    # Check if the difference between current time and world_news_timestamp.json is more than "delay"
                    # seconds then get news from the scraper
                    self.__logger.debug(f"Count of {scraper.address}:"
                                        f" {len(a_bot_controller.bot_model.world_news_dict)}")
                    self.__logger.debug(f"Sleeping in get_world_news on {delay}...")
                    self.__lock.notify_all()
                    self.__logger.debug(f"End of task {scraper.address}")
                self.__waiting_for_finish_the_program_or_timeout(delay)

    def __waiting_for_finish_the_program_or_timeout(self, delay):
        t0 = time.time()
        while self.__program_state_controller.is_program_running() and time.time() - t0 < delay:
            self.__lock.wait(delay)
