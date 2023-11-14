import pickle
import threading
import time
from enum import Enum
from typing import Dict

from news_handling.news_scraper import UANewsScraper, WorldNewsScraper
from core.bot_mvc import BotController
from country_codes.country_codes import CountryCodes
from news_handling.news_article import NewsArticle


# create a class NewsStorage that storages the news by country_codes
class RuntimeNewsStorage:
    def __init__(self):
        self.__news_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {country: None for country in CountryCodes}

    def news_dict(self):
        return self.__news_dict

    def add_news(self, country: CountryCodes, timestamp: float, news_list: list[NewsArticle]) -> None:
        timestamp_news_dict = {timestamp: news_list}
        self.__news_dict[country] = timestamp_news_dict

    def get_news_list(self, country: CountryCodes) -> (float, list[NewsArticle]):
        return self.__news_dict.get(country, [])


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller, logger, update_period: int = 60):
        self.__scrapers = [WorldNewsScraper(logger), UANewsScraper(logger)]
        self.__lock = condition_lock
        self.__program_state_controller = program_state_controller
        self.__is_program_running = self.__program_state_controller.is_program_running
        self.__logger = logger
        self.__runtime_news_storage = RuntimeNewsStorage()
        self.__update_period = update_period

    def get_news(self, a_bot_controller: BotController, delay: int = 60):
        while self.__is_program_running():
            for scraper in self.__scrapers:
                with self.__lock:
                    self.__logger.debug("In task get_world_news")
                    country = scraper.country
                    # timestamp, news_list = self.__runtime_news_storage.get_news_list(country)

                    # TODO: make something with timestamp
                    self.__logger.debug(f"Loading {country} news...")
                    filename = f"{country}-news.pkl"
                    timestamp_news_list_tuple = NewsManager.load_news_from_pkl(filename)

                    if not timestamp_news_list_tuple:
                        timestamp, news_list = scraper.load_news()
                        NewsManager.save_news_to_pkl(filename, timestamp, news_list)
                    timestamp, news_list = timestamp_news_list_tuple
                    self.__runtime_news_storage.add_news(country, timestamp, news_list)

                    # self.__logger.debug(f"Count of {scraper.address}:"
                    #                     f" {len(a_bot_controller.bot_model.world_news_dict)}")
                    self.__logger.debug(f"Sleeping in get_news on {self.__update_period}...")
                    self.__lock.notify_all()
                    self.__logger.debug(f"End of task {scraper.address}")
                    self.__waiting_for_finish_the_program_or_timeout(delay)

    def __waiting_for_finish_the_program_or_timeout(self, delay):
        t0 = time.time()
        while self.__program_state_controller.is_program_running() and time.time() - t0 < delay:
            self.__lock.wait(delay)

    @staticmethod
    def save_news_to_pkl(filename, timestamp: float, news_list: list[NewsArticle]):
        news_tuple = (timestamp, news_list)
        with open(filename, "wb") as file:
            pickle.dump(news_tuple, file)

    @staticmethod
    # returns dict in form {timestamp: list[NewsArticle]}
    def load_news_from_pkl(filename) -> (float, list[NewsArticle]):
        try:
            with open(filename, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    # Create a method that checks if news are updated by differ between current timestamp and timestamp of news in
    # storage
    def check_news_updates(self, country: CountryCodes):
        if time.time() - self.__runtime_news_storage.news_dict()[country][0] > self.__update_period:
            return True
        else:
            return False

