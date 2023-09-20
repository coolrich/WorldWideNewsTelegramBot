import pprint
import sys

import telebot
from telebot import types
from collections import deque
from telebot.formatting import escape_markdown
from requests.exceptions import ReadTimeout
from news_scraper import NewsScraper
import os
from dotenv import load_dotenv


# TODO: Create different news instances for different users.

class BotManager:
    def __init__(self):
        load_dotenv(dotenv_path="./.env")
        token = os.getenv("API_KEY")
        self.bot = telebot.TeleBot(token)
        self.markup = None
        self.world_news_dict = None
        # self.ua_news_dict = None
        self.world_news_deque = None
        # self.ua_news_deque = None
        self.news_manager = NewsManager()
        self.user_news_deqs_dict = {}
        self.ua_news_dict = self.news_manager.get_ua_news()
        self.world_news_dict = self.news_manager.get_world_news()

    def start(self):

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

        @self.bot.message_handler(func=lambda message: message.text == 'Новини України')
        def ua_news_handler(message):
            chat_id = message.chat.id
            ua_news_deque = get_news_deqs(chat_id)['ua']
            title = ua_news_deque[0] if ua_news_deque else None
            if title is None:
                self.bot.send_message(chat_id=message.chat.id, text='Більше новин BBC немає\! Починаємо з початку:',
                                      parse_mode="MarkdownV2")
                # Implementation of repeat news
                return
            post = get_news_info(self.ua_news_dict, ua_news_deque, title)
            self.bot.send_message(chat_id=message.chat.id, text=post, parse_mode="MarkdownV2")

        @self.bot.message_handler(func=lambda message: message.text == 'Новини Світу')
        def world_news_handler(message):
            chat_id = message.chat.id
            world_news_deque = get_news_deqs(chat_id)['en']
            title = world_news_deque[0] if world_news_deque else None
            if title is None:
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Більше новин BBC Ukraine немає\!\n Починаємо з початку:',
                                      parse_mode="MarkdownV2")
                # Implementation of repeat news
                # self.user_news_deqs_dict[chat_id]['en'] = deque(self.world_news_dict)
                # title =
                return
            post = get_news_info(self.world_news_dict, world_news_deque, title)
            self.bot.send_message(chat_id=message.chat.id, text=post, parse_mode="MarkdownV2")

        def get_news_deqs(chat_id):
            if chat_id not in self.user_news_deqs_dict:
                self.user_news_deqs_dict[chat_id] = {'en': deque(self.world_news_dict),
                                                     'ua': deque(self.ua_news_dict)}
            return self.user_news_deqs_dict[chat_id]

        @self.bot.message_handler(func=lambda message: True)
        def default_handler(message):
            self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню нижче:",
                              reply_markup=self.markup)

        self.bot.polling()


class NewsManager:
    def __init__(self):
        self.scraper = NewsScraper()

    def get_world_news(self):
        return self.scraper.get_test_world_news()
        # return self.scraper.get_world_news()

    def get_ua_news(self):
        return self.scraper.get_test_ua_news()
        # return self.scraper.get_ua_news()


class ErrorHandler:
    @staticmethod
    def handle_read_timeout_error(e):
        print(e)


if __name__ == '__main__':
    # print(os.getenv("API_KEY"))
    # sys.exit()
    bot_manager = BotManager()
    while True:
        try:
            bot_manager.start()
        except ReadTimeout as rt:
            ErrorHandler.handle_read_timeout_error(rt)
