# API key: 6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y
# t.me/EarthNewsEpicBot
import pprint
import telebot
from telebot import types
import markdown2
# from faker import Faker
import news_scraper
from collections import deque
import html
from telegram.helpers import escape_markdown

markup = None
bot = telebot.TeleBot("6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y")
bot_username = "@EarthNewsEpicBot"


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Create a keyboard
    global markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Новини'))
    bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Новини')
def echo_all(message):
    news_handler(message)


def news_handler(message):
    print("In news handler.")

    title = news_deque.popleft()
    text = news_dict[title]
    post = '## ' + title + '\n' + text
    post = escape_markdown(post, version=2)
    notification = f"Новини про \n {post}!"
    print(notification)
    bot.send_message(message.chat.id, post, reply_markup=markup, parse_mode='MarkdownV2')


def logging(message):
    pprint.pp(f"Message in console:")
    pprint.pp(message.text)


if __name__ == '__main__':
    news_dict = news_scraper.get_news()
    news_deque = deque(news_dict)
    # fake_gen = Faker()
    bot.polling()
