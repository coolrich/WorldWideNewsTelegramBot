import telebot
from bot_model import BotModel
from bot_view import BotView
from telebot.types import ReplyKeyboardMarkup, Message
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn
import logging
from navigation_menu import Navigator

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
        logger.debug("In handle_message method in BotController class")
        # chat_id = message["chat"]["id"]
        text = message["text"]
        navigator = self.bot_model.get_navigator()
        if text == '/start':
            navigator = self.bot_model.reset_bot()
            results = navigator.get_results_buffer()
            print("Results:", results)
            self.__send_welcome(navigator, message)
        else:
            self.__send_message(navigator, message)
        
        logger.debug("End of the start() method in BotController class")

    def __send_welcome(self, navigator: Navigator, message):
        chat_id = message["chat"]["id"]
        keyboard = navigator.get_keyboard()
        item_name = navigator.get_item_name()
        self.bot.send_message(
            chat_id=chat_id,
            text=f"Привіт, я бот для Telegram, який показує новини\n{item_name}",
            reply_markup=keyboard)

    def __send_message(self, navigator: Navigator, message: Message):
        is_changed, results = navigator.goto(message)
        print("Is menu changed:", is_changed, "\nResults:", results)
        if is_changed:
            keyboard = navigator.get_keyboard()
            self.bot.send_message(message["chat"]["id"], results[0], reply_markup=keyboard, parse_mode='MarkdownV2')

    # def __get_data(self, chat_id: int, text: str):
        # return self.bot_model.get_data(chat_id, text)

    def __default_handler(self, chat_id: int):
        self.bot.send_message(
            chat_id=chat_id,
            text="Я не розумію, що ви хочете сказати. Використовуйте меню нижче:",
            reply_markup=self.bot_view.create_markup())
