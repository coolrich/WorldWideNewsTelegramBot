import threading

import telebot
from requests import ReadTimeout

from controllers.program_state_controller import program_state_controller as psc
from core.bot_model import BotModel
from core.bot_view import BotView
from wwntgbotlib.keyboard_button_names import KeyboardButtonsNames as kbn
from error_handling.error_handler import ErrorHandler


class BotController:

    def __init__(self, a_lock, a_logger):
        self.logger = a_logger
        self.bot_model = BotModel(a_lock, self.logger)
        self.bot_view = BotView()
        self.bot = telebot.TeleBot(self.bot_model.token, exception_handler=BotController.MyBotPollingException(
            self.logger))

    class MyBotPollingException(telebot.ExceptionHandler):
        def __init__(self, a_logger):
            self.logger = a_logger

        def handle(self, exception):
            import traceback
            traceback.print_exc()
            return True

    def start(self):
        lock: threading.Condition = self.bot_model.lock
        with lock:
            self.logger.debug("In start method in BotController class")
            self.create_handlers()
            self.logger.info("Checking for news initialization...")
            # self.is_news_available(lock)
            # Delete webhook
            self.bot.delete_webhook()
        self.bot.polling(long_polling_timeout=2)
        with lock:
            self.logger.info("Bot polling has been started...")
            self.__block_until_program_finish(lock)
        self.logger.debug("End of the start() method in BotController class")

    def is_news_available(self, lock):
        is_news_ready = self.bot_model.is_news_ready
        while not is_news_ready():
            self.logger.info("News are not ready. Waiting for news initialization...")
            lock.notify_all()
            lock.wait_for(is_news_ready)

    def create_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            self.bot.reply_to(message, "Привіт, я бот для Telegram, який показує новини",
                              reply_markup=self.bot_view.create_markup())

        @self.bot.message_handler(
            func=lambda message: message.text in [kbn.UA.value, kbn.WORLD.value])
        def send_news(message):
            data = __get_data(message)
            self.bot.send_message(chat_id=data['chat_id'],
                                  text=data['post'],
                                  parse_mode=data['parse_mode']
                                  )

        def __get_data(message):
            return self.bot_model.get_data(message)

        @self.bot.message_handler(func=lambda message: True)
        def default_handler(message):
            self.bot.reply_to(message, "Я не розумію, що ви хочете сказати. Використовуйте меню "
                                       "нижче:",
                              reply_markup=self.bot_view.create_markup())

    @staticmethod
    def __block_until_program_finish(lock):
        while psc.get_program_state():
            lock.wait_for(lambda: not psc.get_program_state())

    @staticmethod
    def start_bot(a_bot_controller: "BotController"):
        get_program_state = psc.get_program_state
        while get_program_state():
            try:
                a_bot_controller.logger.info("Starting bot controller...")
                a_bot_controller.start()
            except ReadTimeout as rt:
                a_bot_controller.logger.error(
                    "In ReadTimeout Exception handler of start_bot_controller() static method")
                ErrorHandler.handle_read_timeout_error(rt, a_bot_controller.logger)

    @staticmethod
    def stop_bot(a_bot_controller: "BotController"):
        lock = psc.get_condition()
        with lock:
            while psc.get_program_state():
                a_bot_controller.logger.debug("In lock before wait in stop_bot()")
                lock.wait()
        a_bot_controller.bot.stop_polling()
        a_bot_controller.logger.info("Bot stopped")
