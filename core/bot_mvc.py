import os
import threading
from collections import deque
from enum import Enum
from typing import Dict

import telebot

from country_codes.country_codes import CountryCodes
from error_handling.error_handler import ErrorHandler
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from telebot import types
from telebot.formatting import escape_markdown

from news_handling.news_article import NewsArticle
from news_handling.news_manager import RuntimeNewsStorage


# Create a User class that holds the user's data: chat_id, news_dicts_dict,
class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.news_articles_dicts: Dict[CountryCodes, list[NewsArticle]] = {}

    def __eq__(self, chat_id):
        if isinstance(chat_id, int):
            return chat_id == self.chat_id
        return False

    def get_news_article(self, country_code: CountryCodes):
        articles_list = self.news_articles_dicts[country_code]
        if not articles_list:
            self.news_articles_dicts[country_code] = RuntimeNewsStorage().get_news(country_code)
        news_article = articles_list.pop(0)
        articles_list.append(news_article)
        return news_article


        return None


class Users:
    users: set[User] = set()

    @staticmethod
    def get_user(chat_id: int):
        for user in Users.users:
            if user == chat_id:
                return user

    @staticmethod
    def add_user(chat_id: int):
        Users.users.add(User(chat_id))


class BotModel:
    def __init__(self, a_news_manager, a_lock, logger):
        load_dotenv(dotenv_path="../.env")
        self.token = os.getenv("API_KEY")
        self.lock = a_lock
        self.news_manager = a_news_manager
        self.logger = logger
        self.users_storage = Users

    def get_data_from_message(self, message: types.Message):
        parse_mode = 'MarkdownV2'
        chat_id = message.chat.id
        message_text = message.text

        if chat_id in self.users_storage.users:
            user = self.users_storage.get_user(chat_id)
            # TODO: Continue from here
            user.get_news_article(CountryCodes(message_text))
        else:
            self.users_storage.add_user(chat_id)

    def check_news_init(self):
        pass


class BotView:
    def __init__(self):
        self.__markup = None

    @staticmethod
    def get_news_info(news_dict, news_deque, title):
        article_info = news_dict[title]
        text = article_info[0]
        url = article_info[1]
        txt_len = len(text)
        notification = f"{'-' * txt_len}\nНовини про:\nЗаголовок: {title}\nТекст: {text}\nUrl: {url}!\n{'-' * txt_len}"
        title = f'*{escape_markdown(title)}*'
        text = escape_markdown(text)
        url = f'[Посилання на статтю]({url})'
        post = f'{title}\n\n{text}\n\n{url}'
        news_deque.popleft()
        return post

    def create_markup(self):
        self.__markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        self.__markup.add(types.KeyboardButton('Новини Світу'))
        self.__markup.add(types.KeyboardButton('Новини України'))
        return self.__markup


class BotController:
    class MyBotPollingException(telebot.ExceptionHandler):
        def __init__(self, logger):
            self.logger = logger

        def handle(self, exception):
            self.logger.error(exception)
            return True

    def __init__(self, a_news_manager, a_lock, program_state_controller, logger):
        self.logger = logger
        self.bot_model = BotModel(a_news_manager, a_lock, self.logger)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(self.bot_model.token, exception_handler=BotController.MyBotPollingException(
            self.logger))
        self.program_state_controller = program_state_controller

    def start(self):
        lock = self.bot_model.lock
        psc = self.program_state_controller
        with lock:
            self.logger.debug("In start")

            @self.bot.message_handler(commands=['start', 'help'])
            def send_welcome(message):
                self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини",
                                  reply_markup=self.bot_view.create_markup())

            @self.bot.message_handler(
                func=lambda message: message.__text in ['Новини України', 'Новини Світу'])
            def send_news(message):
                data = self.bot_model.get_data_from_message(message)
                self.bot.send_message(chat_id=data['chat_id'],
                                      text=data['post'],
                                      parse_mode=data['parse_mode']
                                      )

            @self.bot.message_handler(func=lambda message: True)
            def default_handler(message):
                self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню "
                                           "нижче:",
                                  reply_markup=self.bot_view.create_markup())

            self.logger.info("Checking the availability of news...")
            check_for_news_init = self.bot_model.check_news_init
            # while check_for_news_init():
            while not check_for_news_init():
                lock.wait_for(check_for_news_init)
                lock.notify_all()
            polling_thread = threading.Thread(target=self.bot.polling, args=(False, False, 0, 0, 1))
            polling_thread.start()
            self.logger.info("Bot polling has been started...")
            self.__block_until_program_finish(lock, psc)
        self.logger.debug("End of the start() method in BotController class")

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
