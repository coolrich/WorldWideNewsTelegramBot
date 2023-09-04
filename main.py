# API key: 6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y
# t.me/EarthNewsEpicBot
import pprint
import telebot
from telebot import types
from faker import Faker
import news_scraper
from collections import deque

news_dict = news_scraper.get_news()
news_deque = deque(news_dict)
bot = telebot.TeleBot("6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y")
bot_username = "@EarthNewsEpicBot"
markup = None


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Create a keyboard
    global markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Новини'))
    bot.reply_to(message, "Привіт, я бот для Telegram", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Новини')
def echo_all(message):
    news_handler(message)


def news_handler(message):
    print("In news handler.")

    title = news_deque.popleft()
    text = news_dict[title]
    post = title + '\n' + text

    notification = f"Новини про \n {post}!"
    print(notification)
    bot.reply_to(message, post, reply_markup=markup)


def logging(message):
    pprint.pp(f"Message in console:")
    pprint.pp(message.text)


if __name__ == '__main__':
    fake_gen = Faker()
    bot.polling()
