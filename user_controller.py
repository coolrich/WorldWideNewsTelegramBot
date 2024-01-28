import logging as logger
import pickle
from typing import Dict
from navigation_menu import *

from wwntgbotlib.country_codes import CountryCodes
from wwntgbotlib.news_article import NewsArticle
from wwntgbotlib.news_manager import NewsManager


class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.news_articles_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {}
        # self.__storage_client = storage.Client()
        self.__navigation_users_data_bucket = storage.Client().bucket("navigation_users_data")
        # self.__navigator = get_navigator()        
        
    def __eq__(self, chat_id):
        if isinstance(chat_id, int):
            return chat_id == self.chat_id
        return False

    def get_navigator(self):
        blob = self.navigation_users_data.blob(f"user_{self.chat_id}_nav_data.pickle")
        if blob.exists():
            navigator_pkl = blob.download_as_string()
            navigator: Navigator = pickle.loads(user_nav_data)
            return navigator
        navigator = self.create_navigator()
        return navigator
    
    def reset_navigator(self):
        navigator = self.__create_navigation()
        navigator_pkl = pickle.dumps(navigator)
        blob.upload_from_string(navigator_pkl)
        return navigator

    def save_navigator_state(self):
        navigator = self.get_navigator()
        navigator_pkl = pickle.dumps(navigator)
        blob.upload_from_string(navigator_pkl)
    
    def __create_navigation(self):
        main = Item("Головна")
        news = main.add_next_item("Новини")
        ukraine_news = news.add_next_item("України")
        last_ukraine_news = ukraine_news.add_next_item("Останні")
        past_ukraine_news = ukraine_news.add_next_item("Минулі")
        world_news = news.add_next_item("Світу")
        last_world_news = world_news.add_next_item("Last")
        past_world_news = world_news.add_next_item("Past")
        settings = main.add_next_item("Налаштування")
        last_ukraine_news.add_action(self.get_data)
        last_world_news.add_action(self.get_data)
        return Navigator(main, "Назад")
    
    # TODO: try to make refactoring
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
