import concurrent.futures
import os
import threading
import time
from collections import deque
from typing import Type

import telebot
from dotenv import load_dotenv
from requests.exceptions import ReadTimeout
from telebot import types
from telebot.formatting import escape_markdown

from news_scraper import NewsScraper


class BotModel:
    def __init__(self, a_news_manager, a_lock):
        load_dotenv(dotenv_path="./.env")
        self.token = os.getenv("API_KEY")
        self.lock = a_lock
        self.news_manager = a_news_manager
        self.user_news_deqs_dict = {}
        # self.markup = None
        self.world_news_deque = None
        self.ua_news_dict = None
        self.world_news_dict = None

    def get_news_deqs(self, a_chat_id):
        if a_chat_id not in self.user_news_deqs_dict:
            self.user_news_deqs_dict[a_chat_id] = {
                'en': deque(self.world_news_dict),
                'ua': deque(self.ua_news_dict)}
        return self.user_news_deqs_dict[a_chat_id]

    def get_data_from_message(self, message: types.Message):
        """
        Retrieves the message data for processing.

        Args:
            message (types.Message): The message object containing the data.

        Returns:
            dict: A dictionary containing the chat ID, post content, and parse mode.

        Raises:
            None
        """
        parse_mode = 'MarkdownV2'
        chat_id = message.chat.id
        message_text = message.text
        news_lang = 'ua' if message_text == 'Новини України' else 'en'
        news_deque = self.get_news_deqs(chat_id)[news_lang]
        if not news_deque:
            self.user_news_deqs_dict[chat_id][news_lang] = (
                deque(self.ua_news_dict)) if news_lang == 'ua' else \
                (deque(self.world_news_dict))
            return {'chat_id': chat_id,
                    'post': f'Більше новин BBC {news_lang} немає\!\n Починаємо з початку:',
                    'parse_mode': parse_mode
                    }

        title = news_deque[0] if news_deque else None
        news_dict = self.ua_news_dict if news_lang == 'ua' else self.world_news_dict
        post = BotView.get_news_info(news_dict, news_deque, title)
        return {'chat_id': chat_id,
                'post': post,
                'parse_mode': parse_mode
                }


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
    def __init__(self, a_news_manager, a_lock):
        self.bot_model = BotModel(a_news_manager, a_lock)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(self.bot_model.token)

    def start(self):
        with self.bot_model.lock:
            print("In start")

            @self.bot.message_handler(commands=['start', 'help'])
            def send_welcome(message):
                self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини",
                                  reply_markup=self.bot_view.create_markup())

            @self.bot.message_handler(
                func=lambda message: message.text in ['Новини України', 'Новини Світу'])
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

            print("Bot manager has been starting...")
        self.bot.polling()

    @staticmethod
    def start_bot_manager(a_bot_controller: Type["BotController"]):
        while True:
            try:
                print("Starting bot manager...")
                a_bot_controller.start()
            except ReadTimeout as rt:
                print("In ReadTimeout Exception handler of start_bot_manger() static method")
                ErrorHandler.handle_read_timeout_error(rt)


class NewsManager:
    def __init__(self, lock):
        self.scraper = NewsScraper()
        self.lock = lock

    def get_world_news(self, a_bot_controller: BotController, delay: int = 60):
        while True:
            with self.lock:
                print("In get_world_news")
                a_bot_controller.bot_model.world_news_dict = self.scraper.get_test_world_news()
                print("-" * 50)
                print(f"Count of World news: {len(a_bot_controller.bot_model.world_news_dict)}")
                print("-" * 50)
            print(f"Sleeping in get_world_news on {delay}...")
            time.sleep(delay)

    def get_ua_news(self, a_bot_controller: BotController, delay: int = 60):
        while True:
            with self.lock:
                print("In get_ua_news")
                a_bot_controller.bot_model.ua_news_dict = self.scraper.get_test_ua_news()
                print("-" * 50)
                print(f"Count of UA news: {len(a_bot_controller.bot_model.ua_news_dict)}")
                print("-" * 50)
            print(f"Sleeping in get_ua_news on {delay}...")
            time.sleep(delay)


class ErrorHandler:
    @staticmethod
    def handle_read_timeout_error(e):
        print(e)


class FunctionExecutor:
    def __init__(self, max_workers):
        self.max_workers = max_workers
        # self.interval = interval

    def execute_functions_periodically(self, *functions_with_args):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for func, args in functions_with_args:
                print("function:", func, "args:", args)
                if args is not None:
                    futures.append(executor.submit(func, *args))
                else:
                    futures.append(executor.submit(func))
            print("After for loop in execute_functions_periodically")
            concurrent.futures.wait(futures)
            print("After wait in execute_functions_periodically")
            # time.sleep(60)


class StartTheBot:
    def __init__(self):
        self.lock = threading.Lock()
        self.news_manager = NewsManager(self.lock)
        self.bot_controller = BotController(self.news_manager, self.lock)
        self.function_executor = FunctionExecutor(max_workers=3)

    def start(self):
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_controller, 60,)),
            (self.news_manager.get_world_news, (self.bot_controller, 60,)),
            (self.bot_controller.start_bot_manager, (self.bot_controller,))
        )


if __name__ == "__main__":
    StartTheBot().start()
