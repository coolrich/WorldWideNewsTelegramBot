from telebot import types
from telebot.formatting import escape_markdown

from core.keyboard_button_names import KeyboardButtonsNames as kbn
from news_handling.news_article import NewsArticle


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