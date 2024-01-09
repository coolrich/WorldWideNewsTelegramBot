import os

from dotenv import load_dotenv
from telebot import types

from controllers.program_state_controller import program_state_controller as psc
from core.bot_view import BotView
from core.user_storage import Users
from wwntgbotlib.country_codes import CountryCodes
from google.cloud import secretmanager
from core.user_controller import User


class BotModel:
    def __init__(self, a_lock, a_logger):
        load_dotenv(dotenv_path="../.env")
        # self.token = os.getenv("API_KEY")
        self.token = BotModel.get_secret("worldwidenewstelegrambot", "bot_token")
        self.lock = a_lock
        self.logger = a_logger
        self.users_storage = Users()

    @staticmethod
    def get_secret(project_id, secret_id, version_id="latest"):
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload

    def get_data(self, message: types.Message):
        parse_mode = 'MarkdownV2'
        chat_id = message.chat.id
        message_text = message.text

        self.logger.debug(f"Message: {message_text}")

        user = self.get_user(chat_id)

        # if self.is_new_user(chat_id):
        #     self.add_user(user)

        news_article = self.get_news_article(message_text, user)
        post = BotView.get_post_dict(news_article)
        self.save_user(user)
        return {'chat_id': chat_id, 'post': post, 'parse_mode': parse_mode}

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

    @staticmethod
    def is_news_ready():
        return psc.is_news_ready()
