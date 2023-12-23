import logging as logger
from typing import Dict

from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.news_article import NewsArticle
from wwntgbotlib.news_manager import NewsManager


class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.news_articles_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {}

    def __eq__(self, chat_id):
        if isinstance(chat_id, int):
            return chat_id == self.chat_id
        return False

    def get_news_article(self, country_code: CountryCodes) -> NewsArticle:
        logger.debug(f"In method get_news_article: {country_code}")
        logger.debug(f"In method get_news_article news_articles_dict: {self.news_articles_dict}")
        timestamp, articles_list = self.news_articles_dict.get(country_code, (None, None))
        logger.debug(f"News timestamp: {timestamp}, News article list: {articles_list}")
        if articles_list is None:
            timestamp, articles_list = NewsManager.get_news_data(country_code)
            self.news_articles_dict[country_code] = (timestamp, articles_list)
        logger.debug(f"In get news article: News timestamp: {timestamp}, News article list: {articles_list}")
        logger.debug(f"News article list: {articles_list}")
        if articles_list is None:
            return NewsArticle("", "News are updating, please wait...", "")
        news_article = articles_list.pop(0)
        articles_list.append(news_article)
        return news_article
