# API key: 6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y
# t.me/EarthNewsEpicBot
import pprint
import telebot
from telebot import types
import news_scraper
from collections import deque
from telebot.formatting import escape_markdown

markup = None
bot = telebot.TeleBot(token="6513546283:AAGehuVYsklhpdNNbOGQMU1jwmjg6zVzU-Y")
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
    title = news_deque.popleft() if news_deque else None
    if title is None:
        bot.send_message(chat_id=message.chat.id, text='There are no news!', parse_mode="MarkdownV2")
        return
    text = news_dict[title][0]
    url = news_dict[title][1]
    txt_len = len(text)
    notification = f"{'-' * txt_len}\nНовини про: \ntitle:{title}\ntext:{text}\nurl:{url}!\n{'-' * txt_len}"
    print(notification)
    title = f'*{escape_markdown(title)}*'
    text = escape_markdown(text)
    url = f'[Link to the article]({url})'
    post = f'{title}\n\n{text}\n\n{url}'
    bot.send_message(chat_id=message.chat.id, text=post, parse_mode="MarkdownV2")


def logging(message):
    pprint.pp(f"Message in console:")
    pprint.pp(message.text)


if __name__ == '__main__':
    news_dict = news_scraper.get_news()
    news_deque = deque(news_dict)
    bot.polling()
