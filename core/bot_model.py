import os

from dotenv import load_dotenv
from telebot import types

from core.bot_view import BotView
from core.user_storage import Users
from country_codes.country_codes import CountryCodes
from news_handling.news_manager import NewsManager


class BotModel:
    def __init__(self, a_news_manager: NewsManager, a_lock, a_logger):
        load_dotenv(dotenv_path="../.env")
        self.token = os.getenv("API_KEY")
        self.lock = a_lock
        self.news_manager = a_news_manager
        self.logger = a_logger
        self.users_storage = Users

    def get_data(self, message: types.Message):
        parse_mode = 'MarkdownV2'
        chat_id = message.chat.id
        message_text = message.text

        self.logger.debug(f"Message: {message_text}")

        if self.is_new_user(chat_id):
            self.add_user(chat_id)

        user = self.get_user(chat_id)

        news_article = self.get_news_article(message_text, user)
        post = BotView.get_post_dict(news_article)

        return {'chat_id': chat_id, 'post': post, 'parse_mode': parse_mode}

    def get_news_article(self, message_text, user):
        return user.get_news_article(CountryCodes.get_member_by_value(message_text), self.news_manager)

    def get_user(self, chat_id):
        return self.users_storage.get_user(chat_id)

    def is_new_user(self, chat_id):
        return chat_id not in self.users_storage.users

    def add_user(self, chat_id):
        self.users_storage.add_user(chat_id)

    def are_news_ready(self):
        return self.news_manager.are_news_ready()
