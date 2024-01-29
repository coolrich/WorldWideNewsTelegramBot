import telebot
from bot_model import DataController, NavigatorController
from bot_view import BotView
from telebot.types import ReplyKeyboardMarkup, Message
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn
from navigation_menu import Navigator
import logging 

# Створення логера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Створення обробника консолі
console_handler = logging.StreamHandler()

# Встановлення рівня логування для обробника консолі
console_handler.setLevel(logging.DEBUG)

# Створення об'єкта форматування
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Встановлення форматування для обробника консолі
console_handler.setFormatter(formatter)

# Додавання обробника консолі до логера
logger.addHandler(console_handler)

class BotController:

    def __init__(self, token: str):
        self.data_controller = DataController(logger, token)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(self.data_controller.token, exception_handler=BotController.MyBotPollingException(logger))
        self.navigator_controller = NavigatorController(self.data_controller)

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
        print("Message:", message)
        if text == '/start':
            navigator = self.navigator_controller.reset(message)
            results = navigator.get_results_buffer()
            print("Results:", results)
            self.__send_welcome(navigator, message)
        else:
            navigator = self.navigator_controller.get_navigator(message)
            self.__send_message(navigator, message)
        self.navigator_controller.save_state(navigator, message)
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
        answer = f"{message['text']}\n"
        for result in results:
            answer += str(result) + '\n'
        chat_id = message["chat"]["id"]
        print("Is menu changed:", is_changed, "\nResults:", answer)
        keyboard = navigator.get_keyboard()
        if is_changed:
            self.bot.send_message(chat_id, answer, reply_markup=keyboard, parse_mode='MarkdownV2')
            return
        self.bot.send_message(chat_id, answer, reply_markup=keyboard, parse_mode='MarkdownV2')
        
        
