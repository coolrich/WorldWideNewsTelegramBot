import pickle
import threading
import time
from enum import Enum
from typing import Dict

from news_handling.news_scraper import UANewsScraper, WorldNewsScraper
from country_codes.country_codes import CountryCodes
from news_handling.news_article import NewsArticle
import logging as logger


# create a class NewsStorage that storages the news by country_codes
class RuntimeNewsStorage:
    def __init__(self):
        self.__news_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {}

    def get_news_dict(self):
        return self.__news_dict

    def add_news(self, country: CountryCodes, timestamp: float, news_list: list[NewsArticle]) -> None:
        timestamp_news_tuple = (timestamp, news_list)
        self.__news_dict[country] = timestamp_news_tuple

    def get_timestamp_and_news_articles_list(self, country: CountryCodes) -> (float, list[NewsArticle]):
        logger.debug(f"In get_timestamp_and_news_articles_list country: {country}")
        news_dict = self.__news_dict.get(country, (None, [NewsArticle()]))
        logger.debug(f"In get_timestamp_and_news_articles_list: {news_dict}")
        timestamp, news_list = news_dict
        return timestamp, news_list


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller, a_logger,
                 news_update_period: int = 60):
        self.__scrapers = [WorldNewsScraper(a_logger), UANewsScraper(a_logger)]
        self.__lock = condition_lock
        self.__program_state_controller = program_state_controller
        self.__is_program_running = self.__program_state_controller.is_program_running
        self.__logger = a_logger
        self.__runtime_news_storage = RuntimeNewsStorage()
        self.__news_update_period = news_update_period

    def get_runtime_news_storage(self):
        return self.__runtime_news_storage

    def get_news(self):
        while self.__is_program_running():
            with self.__lock:
                for scraper in self.__scrapers:
                    self.__logger.debug("In task get_news")
                    country_code = scraper.country
                    self.__logger.info(f"Loading {country_code} news...")
                    filename = f"{country_code.name}-news.pkl"
                    timestamp, news_list = self.load_news_from_pkl(filename)
                    self.__logger.debug(f"news list: {news_list}, timestamp: {timestamp}")
                    if news_list is None:
                        self.__logger.info(f"Loading {country_code} news from {scraper.address}...")
                        timestamp, news_list = scraper.load_news()
                        NewsManager.save_news_to_pkl(filename, timestamp, news_list)
                        self.__logger.info(f"News has been saved to {filename}!")
                    self.__runtime_news_storage.add_news(country_code, timestamp, news_list)
                    self.__logger.debug(f"End of task {scraper.address}")
                    self.__logger.debug(f"Sleeping in get_news on {self.__news_update_period}...")
                self.__waiting_for_finish_the_program_or_timeout()

    def __waiting_for_finish_the_program_or_timeout(self):
        t0 = time.time()
        while (time.time() - t0 < self.__news_update_period) and self.__is_program_running():
            self.__lock.notify_all()
            self.__lock.wait(self.__news_update_period)

    @staticmethod
    def save_news_to_pkl(filename, timestamp: float, news_list: list[NewsArticle]):
        news_tuple = (timestamp, news_list)
        with open(filename, "wb") as file:
            pickle.dump(news_tuple, file)

    def load_news_from_pkl(self, filename) -> (float, list[NewsArticle]):
        """
           Load news data from a pickle file.

           Args:
               filename (str): The name of the pickle file.

           Returns:
               A tuple containing the timestamp and a list of NewsArticle objects loaded from the file. If the file is not found,
               an empty tuple is returned.
           """
        timestamp, news_list = (None, None)
        try:
            with open(filename, "rb") as file:
                timestamp, news_list = pickle.load(file)
        except FileNotFoundError:
            self.__logger.debug(f"File {filename} not found.")
        return timestamp, news_list

    # Create a method that checks if news are updated by differ between current timestamp and timestamp of news in
    # storage
    # def check_news_updates(self, country: CountryCodes):
    #     if (time.time() - self.__runtime_news_storage.get_timestamp_and_news_articles_list(country)[0] >
    #             self.__update_period):
    #         return True
    #     else:
    #         return False
