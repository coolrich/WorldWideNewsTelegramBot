import telebot
from telebot import types
from collections import deque
from telebot.formatting import escape_markdown
from requests.exceptions import ReadTimeout
from news_scraper import NewsScraper


class BotManager:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.markup = None
        self.world_news_dict = None
        self.ua_news_dict = None
        self.world_news_deque = None
        self.ua_news_deque = None

    def start(self):
        self.world_news_dict = NewsManager.get_world_news()
        self.ua_news_dict = NewsManager.get_ua_news()
        self.world_news_deque = deque(self.world_news_dict)
        self.ua_news_deque = deque(self.ua_news_dict)

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            self.markup.add(types.KeyboardButton('Новини Світу'))
            self.markup.add(types.KeyboardButton('Новини України'))
            self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини", reply_markup=self.markup)

        @self.bot.message_handler(func=lambda message: message.text == 'Новини України')
        def ua_news_handler(message):
            title = self.ua_news_deque.popleft() if self.ua_news_deque else None
            if title is None:
                self.bot.send_message(chat_id=message.chat.id, text='Більше новин немає\!', parse_mode="MarkdownV2")
                return
            text = self.ua_news_dict[title][0]
            url = self.ua_news_dict[title][1]
            txt_len = len(text)
            notification = f"{'-' * txt_len}\nНовини про:\nЗаголовок: {title}\nТекст: {text}\nUrl: {url}!\n{'-' * txt_len}"
            title = f'*{escape_markdown(title)}*'
            text = escape_markdown(text)
            url = f'[Посилання на статтю]({url})'
            post = f'{title}\n\n{text}\n\n{url}'
            self.bot.send_message(chat_id=message.chat.id, text=post, parse_mode="MarkdownV2")

        @self.bot.message_handler(func=lambda message: message.text == 'Новини Світу')
        def world_news_handler(message):
            title = self.world_news_deque.popleft() if self.world_news_deque else None
            if title is None:
                self.bot.send_message(chat_id=message.chat.id, text='Більше новин немає\!', parse_mode="MarkdownV2")
                return
            text = self.world_news_dict[title][0]
            url = self.world_news_dict[title][1]
            txt_len = len(text)
            notification = f"{'-' * txt_len}\nНовини про: \nЗаголовок: {title}\nТекст: {text}\nUrl: {url}!\n{'-' * txt_len}"
            title = f'*{escape_markdown(title)}*'
            text = escape_markdown(text)
            url = f'[Посилання на статтю]({url})'
            post = f'{title}\n\n{text}\n\n{url}'
            self.bot.send_message(chat_id=message.chat.id, text=post, parse_mode="MarkdownV2")

        @self.bot.message_handler(func=lambda message: True)
        def default_handler(message):
            self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню нижче:",
                              reply_markup=self.markup)

        self.bot.polling()


class NewsManager:
    @staticmethod
    def get_world_news():
        scraper = NewsScraper()
        return scraper.get_world_news()

    @staticmethod
    def get_ua_news():
        scraper = NewsScraper()
        return scraper.get_ua_news()


class ErrorHandler:
    @staticmethod
    def handle_read_timeout_error(e):
        print(e)


if __name__ == '__main__':
    bot_manager = BotManager(token="6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y")
    while True:
        try:
            bot_manager.start()
        except ReadTimeout as rt:
            ErrorHandler.handle_read_timeout_error(rt)
