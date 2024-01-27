from telebot import types
from telebot.formatting import escape_markdown
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn
from wwntgbotlib.news_article import NewsArticle

class BotView:
    def __init__(self):
        self.__markup = None
        
    @staticmethod
    def get_post(news_article: NewsArticle) -> str:
        text = news_article.get_text
        url = news_article.get_url
        title = news_article.get_title
        # txt_len = len(text)
        # notification = f"{'-' * txt_len}\nНовини про:\nЗаголовок: {title}\nТекст: {text}\nUrl: {url}!\n{'-' * txt_len}"
        title = f'*{escape_markdown(title)}*'
        text = escape_markdown(text)
        url_text = '[Посилання на статтю]'
        if url != "":
            url = f'{url_text}({url})'
        else:
            url = ""
        post = f'{title}\n\n{text}\n\n{url}'
        return post

    # def create_markup(self):
        # self.__markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        # self.__markup.add(types.KeyboardButton(kbn.UA.value))
        # self.__markup.add(types.KeyboardButton(kbn.WORLD.value))
        # return self.__markup
