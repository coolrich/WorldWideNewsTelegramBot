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
    
    def get_navigator(self, message):
        chat_id = message['chat']['id']
        return self.get_user(chat_id).get_navigator()
    
    def reset_navigator(self, message):
        chat_id = message['chat']['id']
        return self.get_user(chat_id).reset_navigator()
    
    def save_navigator_state(self, message):
        chat_id = message['chat']['id']
        return self.get_user(chat_id).create_navigator()
    
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
