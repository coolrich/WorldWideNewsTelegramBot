import os
import threading
from typing import Dict

import telebot

from error_handling.error_handler import ErrorHandler
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from telebot import types
from telebot.formatting import escape_markdown
from country_codes.country_codes import CountryCodes

from news_handling.news_article import NewsArticle
from news_handling.news_manager import NewsManager
import logging as logger
from core.keyboard_button_names import KeyboardButtonsNames as kbn


# TODO: test the program and make refactoring after successful tests
class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.news_articles_dict: Dict[CountryCodes, (float, list[NewsArticle])] = {}

    def __eq__(self, chat_id):
        if isinstance(chat_id, int):
            return chat_id == self.chat_id
        return False

    def get_news_article(self, country_code: CountryCodes, news_manager: NewsManager) -> NewsArticle:
        logger.debug(f"In method get_news_article: {country_code}")
        logger.debug(f"In method get_news_article news_articles_dict: {self.news_articles_dict}")
        timestamp, articles_list = self.news_articles_dict.get(country_code, (None, None))
        logger.debug(f"News timestamp: {timestamp}, News article list: {articles_list}")
        if articles_list is None:
            runtime_news_storage = news_manager.get_runtime_news_storage()
            timestamp, articles_list = (runtime_news_storage.get_timestamp_and_news_articles_list(country_code))
            self.news_articles_dict[country_code] = (timestamp, articles_list)
        logger.debug(f"In get news article: News timestamp: {timestamp}, News article list: {articles_list}")
        logger.debug(f"News article list: {articles_list}")
        news_article = articles_list.pop(0)
        articles_list.append(news_article)
        return news_article


class Users:
    users: list[User] = list()

    @staticmethod
    def get_user(chat_id: int):
        for user in Users.users:
            if user == chat_id:
                return user

    @staticmethod
    def add_user(chat_id: int):
        Users.users.append(User(chat_id))


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


class BotView:

    def __init__(self):
        self.__markup = None

    @staticmethod
    def get_post_dict(news_article: NewsArticle):
        text = news_article.get_text
        url = news_article.get_url
        title = news_article.get_title
        # txt_len = len(text)
        # notification = f"{'-' * txt_len}\nНовини про:\nЗаголовок: {title}\nТекст: {text}\nUrl: {url}!\n{'-' * txt_len}"
        title = f'*{escape_markdown(title)}*'
        text = escape_markdown(text)
        url = f'[Посилання на статтю]({url})'
        post = f'{title}\n\n{text}\n\n{url}'
        return post

    def create_markup(self):
        self.__markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        self.__markup.add(types.KeyboardButton(kbn.UA.value))
        self.__markup.add(types.KeyboardButton(kbn.WORLD.value))
        return self.__markup


class BotController:

    def __init__(self, a_news_manager, a_lock, program_state_controller, a_logger):
        self.logger = a_logger
        self.bot_model = BotModel(a_news_manager, a_lock, self.logger)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(self.bot_model.token, exception_handler=BotController.MyBotPollingException(
            self.logger))
        self.program_state_controller = program_state_controller

    class MyBotPollingException(telebot.ExceptionHandler):
        def __init__(self, a_logger):
            self.logger = a_logger

        def handle(self, exception):
            import traceback
            traceback.print_exc()
            return True

    def start(self):
        lock = self.bot_model.lock
        psc = self.program_state_controller
        with lock:
            self.logger.debug("In start method in BotController class")
            self.create_handlers()
            self.logger.info("Checking for news initialization...")
            self.is_news_available(lock)
            self.start_polling()
            self.logger.info("Bot polling has been started...")
            self.__block_until_program_finish(lock, psc)
        self.logger.debug("End of the start() method in BotController class")

    def start_polling(self):
        polling_thread = threading.Thread(target=self.bot.polling, args=(False, False, 0, 0, 20))
        polling_thread.start()

    def is_news_available(self, lock):
        are_news_ready = self.bot_model.are_news_ready
        while not are_news_ready():
            self.logger.info("News are not ready. Waiting for news initialization...")
            lock.notify_all()
            lock.wait_for(are_news_ready)

    def create_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини",
                              reply_markup=self.bot_view.create_markup())

        @self.bot.message_handler(
            func=lambda message: message.text in [kbn.UA.value, kbn.WORLD.value])
        def send_news(message):
            data = __get_data(message)
            self.bot.send_message(chat_id=data['chat_id'],
                                  text=data['post'],
                                  parse_mode=data['parse_mode']
                                  )

        def __get_data(message):
            return self.bot_model.get_data(message)

        @self.bot.message_handler(func=lambda message: True)
        def default_handler(message):
            self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню "
                                       "нижче:",
                              reply_markup=self.bot_view.create_markup())

    @staticmethod
    def __block_until_program_finish(lock, psc):
        while psc.is_program_running():
            lock.wait_for(lambda: not psc.is_program_running())

    @staticmethod
    def start_bot(a_bot_controller: "BotController"):
        get_program_state = a_bot_controller.program_state_controller.is_program_running
        while get_program_state():
            try:
                a_bot_controller.logger.info("Starting bot controller...")
                a_bot_controller.start()
            except ReadTimeout as rt:
                a_bot_controller.logger.error(
                    "In ReadTimeout Exception handler of start_bot_controller() static method")
                ErrorHandler.handle_read_timeout_error(rt, a_bot_controller.logger)

    @staticmethod
    def stop_bot(a_bot_controller: "BotController"):
        lock = a_bot_controller.program_state_controller.get_condition()
        psc = a_bot_controller.program_state_controller
        with lock:
            while psc.is_program_running():
                a_bot_controller.logger.debug("In lock before wait in stop_bot()")
                lock.wait()
        a_bot_controller.bot.stop_polling()
        a_bot_controller.logger.info("Bot stopped")
