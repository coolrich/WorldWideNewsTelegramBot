import json
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
        self.__news_dict: Dict[CountryCodes, list[NewsArticle]] = {country: [] for country in CountryCodes}

    def news_dict(self):
        return self.__news_dict

    def add_news(self, country: CountryCodes, news_list: list[NewsArticle]):
        """
        Adds news to the news dictionary for a given country.

        Parameters:
            country (CountryCodes): The country code for which the news is being added.
            news_list (list): A list of news items to be added.

        Returns:
            None
        """
        self.__news_dict[country] = news_list

    def get_news(self, country: CountryCodes):
        return self.__news_dict.get(country, [])


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller, logger):
        self.__scrapers = [WorldNewsScraper(logger), UANewsScraper(logger)]
        self.__lock = condition_lock
        self.__program_state_controller = program_state_controller
        self.__is_program_running = self.__program_state_controller.is_program_running
        self.__logger = logger
        self.runtime_news_storage = RuntimeNewsStorage()

    def get_news(self, a_bot_controller: BotController, delay: int = 60):
        while self.__is_program_running():
            for scraper in self.__scrapers:
                with self.__lock:
                    self.__logger.debug("In task get_world_news")
                    country = scraper.country
                    filename = f"{country}-news.json"
                    news_dict = NewsManager.load_from_json(filename)
                    if not news_dict:
                        news_list = scraper.load_news()
                        NewsManager.save_to_json(filename, news_list)
                    else:
                        news_list = news_dict[country]
                    self.runtime_news_storage.add_news(country, news_list)

                    # self.__logger.debug(f"Count of {scraper.address}:"
                    #                     f" {len(a_bot_controller.bot_model.world_news_dict)}")
                    self.__logger.debug(f"Sleeping in get_news on {delay}...")
                    self.__lock.notify_all()
                    self.__logger.debug(f"End of task {scraper.address}")
                self.__waiting_for_finish_the_program_or_timeout(delay)

    def __waiting_for_finish_the_program_or_timeout(self, delay):
        t0 = time.time()
        while self.__program_state_controller.is_program_running() and time.time() - t0 < delay:
            self.__lock.wait(delay)

    @staticmethod
    def save_to_json(filename, news_dict: Dict[CountryCodes, list[NewsArticle]]):
        with open(filename, "w") as file:
            json.dump(news_dict, file)

    @staticmethod
    def load_from_json(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return None
