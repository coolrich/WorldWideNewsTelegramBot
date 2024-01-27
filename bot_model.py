# from telebot import types
from bot_view import BotView
from user_storage import Users
from wwntgbotlib.country_codes import CountryCodes
from user_controller import User
from navigation_menu import *

class BotModel:
    def __init__(self, a_logger, token):
        self.token = token
        self.logger = a_logger
        self.users_storage = Users()      
        self.__navigator = self.__create_navigation()
        
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

    def get_navigator(self):
        return self.__navigator
    
    def reset_bot(self):
        self.__navigator = self.__create_navigation()
        return self.__navigator
    
    def get_data(self, message):
        char_id = message["chat"]["id"]
        parse_mode = 'MarkdownV2'
        message_text = message["text"]

        self.logger.debug(f"Message: {message_text}")
        user = self.get_user(chat_id)
        if user is None:
            self.add_user(chat_id)
            user = self.get_user(chat_id)
        news_article = self.get_news_article(message_text, user)
        post = BotView.get_post(news_article)
        self.save_user(user)
        return post

    @staticmethod
    def get_news_article(message_text, user: User):
        return user.get_news_article(CountryCodes.get_member_by_value(message_text))

    def get_user(self, chat_id):
        return self.users_storage.get_user(chat_id)

    def is_new_user(self, chat_id):
        # return chat_id not in self.users_storage.users
        return self.users_storage.get_user(chat_id) is None

    def save_user(self, user: User):
        self.users_storage.add_user(user)

    def add_user(self, chat_id):
        self.users_storage.add_user(User(chat_id))
