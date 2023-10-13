from typing import Type
import pprint
import sys
import concurrent.futures
import time
import threading
import telebot
from telebot import types
from collections import deque
from telebot.formatting import escape_markdown
from requests.exceptions import ReadTimeout
from news_scraper import NewsScraper
import os
from dotenv import load_dotenv


# Developing of  parallel execution of users message handling and news parsing.
class BotManager:
    def __init__(self, a_news_manager, a_lock):
        self.lock = a_lock
        load_dotenv(dotenv_path="./.env")
        token = os.getenv("API_KEY")
        self.bot = telebot.TeleBot(token)
        self.markup = None
        self.world_news_dict = None
        # self.ua_news_dict = None
        self.world_news_deque = None
        # self.ua_news_deque = None
        self.news_manager = a_news_manager
        self.user_news_deqs_dict = {}
        self.ua_news_dict = None
        self.world_news_dict = None

    def start(self):
        # self.news_manager.get_ua_news(self)
        # self.news_manager.get_world_news(self)
        with self.lock:
            print("In start")

            @self.bot.message_handler(commands=['start', 'help'])
            def send_welcome(message):
                self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                self.markup.add(types.KeyboardButton('Новини Світу'))
                self.markup.add(types.KeyboardButton('Новини України'))
                self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини", reply_markup=self.markup)

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

            @self.bot.message_handler(func=lambda message: message.text in ['Новини України', 'Новини Світу'])
            def news_handler(message):
                chat_id = message.chat.id
                news_type = message.text
                news_lang = 'ua' if news_type == 'Новини України' else 'en'
                news_deque = get_news_deqs(chat_id)[news_lang]

                while not news_deque:
                    self.bot.send_message(chat_id=chat_id,
                                          text=f'Більше новин BBC {news_lang} немає\!\n Починаємо з початку:',
                                          parse_mode="MarkdownV2")
                    self.user_news_deqs_dict[chat_id][news_lang] = deque(
                        self.ua_news_dict) if news_lang == 'ua' else deque(
                        self.world_news_dict)
                    news_deque = get_news_deqs(chat_id)[news_lang]

                title = news_deque[0] if news_deque else None
                news_dict = self.ua_news_dict if news_lang == 'ua' else self.world_news_dict
                post = get_news_info(news_dict, news_deque, title)
                self.bot.send_message(chat_id=chat_id, text=post, parse_mode="MarkdownV2")

            def get_news_deqs(chat_id):
                if chat_id not in self.user_news_deqs_dict:
                    self.user_news_deqs_dict[chat_id] = {'en': deque(self.world_news_dict),
                                                         'ua': deque(self.ua_news_dict)}
                return self.user_news_deqs_dict[chat_id]

            @self.bot.message_handler(func=lambda message: True)
            def default_handler(message):
                self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню нижче:",
                                  reply_markup=self.markup)

            print("Bot manager has been starting...")
            self.bot.polling()

    @staticmethod
    def start_bot_manager(a_bot_manager: Type["BotManager"]):
        while True:
            try:
                print("Starting bot manager...")
                a_bot_manager.start()
            except ReadTimeout as rt:
                print("In ReadTimeout Exception handler of start_bot_manger() static method")
                ErrorHandler.handle_read_timeout_error(rt)


class NewsManager:
    def __init__(self, lock):
        self.scraper = NewsScraper()
        self.lock = lock

    def get_world_news(self, a_bot_manager: BotManager, delay: int = 60):
        while True:
            with self.lock:
                print("In get_world_news")
                a_bot_manager.world_news_dict = self.scraper.get_test_world_news()
                print("-"*50)
                print(f"Count of World news: {len(a_bot_manager.world_news_dict)}")
                print("-"*50)
            print(f"Sleeping in get_world_news on {delay}...")
            time.sleep(delay)
        # return self.scraper.get_test_world_news()
        # return self.scraper.get_world_news()

    def get_ua_news(self, a_bot_manager: BotManager, delay: int = 60):
        while True:
            with self.lock:
                print("In get_ua_news")
                a_bot_manager.ua_news_dict = self.scraper.get_test_ua_news()
                print("-"*50)
                print(f"Count of UA news: {len(a_bot_manager.ua_news_dict)}")
                print("-"*50)
            print(f"Sleeping in get_ua_news on {delay}...")
            time.sleep(delay)
    # return self.scraper.get_test_ua_news()
    # return self.scraper.get_test_ua_news()
    # return self.scraper.get_ua_news()


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
            concurrent.futures.wait(futures)
            # time.sleep(60)


class StartTheBot:
    def __init__(self):
        self.lock = threading.Lock()
        self.news_manager = NewsManager(self.lock)
        self.bot_manager = BotManager(self.news_manager, self.lock)
        self.function_executor = FunctionExecutor(max_workers=3)

    def start(self):
        self.function_executor.execute_functions_periodically(
            (self.news_manager.get_ua_news, (self.bot_manager, 60,)),
            (self.news_manager.get_world_news, (self.bot_manager, 60,)),
            (self.bot_manager.start_bot_manager, (self.bot_manager,))
        )


if __name__ == "__main__":
    StartTheBot().start()
