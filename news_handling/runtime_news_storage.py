import logging as logger
from typing import Dict

from country_codes.country_codes import CountryCodes
from news_handling.news_article import NewsArticle


class RuntimeNewsStorage:
    def __init__(self):
        self.__news_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {}
        self.__timestamp_of_last_save = 0

    def get_news_dict(self):
        return self.__news_dict

    def add_news(self, country: CountryCodes, timestamp: float, news_list: list[NewsArticle]) -> None:
        self.__news_dict[country] = (timestamp, news_list)
        if self.__timestamp_of_last_save == 0:
            self.__timestamp_of_last_save = timestamp
        logger.debug(f"News for {country} has been added to storage")

    def get_timestamp_and_news_articles_list(self, country: CountryCodes) -> (float, list[NewsArticle]):
        logger.debug(f"In get_timestamp_and_news_articles_list country: {country}")
        news_dict = self.__news_dict.get(country, (None, [NewsArticle()]))
        logger.debug(f"In get_timestamp_and_news_articles_list: {news_dict}")
        timestamp, news_list = news_dict
        return timestamp, news_list

    def get_last_timestamp(self):
        return self.__timestamp_of_last_save

    def reset_last_timestamp(self):
        self.__timestamp_of_last_save = 0

    def set_last_timestamp(self, timestamp):
        self.__timestamp_of_last_save = timestamp
