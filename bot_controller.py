import telebot
from bot_model import BotModel
from bot_view import BotView
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn
import logging

logger = logging.getLogger(__name__)


class BotController:

    def __init__(self, token: str):
        self.bot_model = BotModel(logger, token)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(
            self.bot_model.token, exception_handler=BotController.MyBotPollingException(logger)
        )

    class MyBotPollingException(telebot.ExceptionHandler):
        def __init__(self, a_logger):
            self.logger = a_logger

        def handle(self, exception):
            import traceback
            traceback.print_exc()
            return True

    def handle_message(self, message: telebot.types.Message):
        logger.debug("In start method in BotController class")
        chat_id = message["chat"]["id"]
        text = message["text"]
        if text in ['/start', '/help']:
            self.__send_welcome(chat_id)
        elif text in [kbn.UA.value, kbn.WORLD.value]:
            self.__send_news(chat_id, text)
        else:
            self.__default_handler(chat_id)
        logger.debug("End of the start() method in BotController class")

    def __send_welcome(self, chat_id: int):
        self.bot.send_message(
            chat_id=chat_id,
            text="Привіт, я бот для Telegram, який показує новини",
            reply_markup=self.bot_view.create_markup())

    def __send_news(self, chat_id: int, text: str):
        data = self.__get_data(chat_id, text)
        self.bot.send_message(chat_id=data['chat_id'],
                              text=data['post'],
                              parse_mode=data['parse_mode']
                              )

    def __get_data(self, chat_id: int, text: str):
        return self.bot_model.get_data(chat_id, text)

    def __default_handler(self, chat_id: int):
        self.bot.send_message(
            chat_id=chat_id,
            text="Я не розумію, що ви хочете сказати. Використовуйте меню нижче:",
            reply_markup=self.bot_view.create_markup())