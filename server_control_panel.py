import os
import signal

from flask import Flask, render_template
from controllers.application_controller import ApplicationController

# TODO: Add authentication with login and password

# Змінна-флаг для вказування на стан бота (активний або призупинений)
bot_active = False

# Створіть веб-сервер Flask
bot = ApplicationController()
flask_app = Flask(__name__)


# Обробник головної сторінки
@flask_app.route('/')
def index():
    return render_template('index.html')


# Обробник для команди запуску бота
@flask_app.route('/start_bot')
def start_bot():
    global bot_active

    if not bot_active:
        bot.start()
        bot_active = True

    return "Bot started!"


# Обробник для команди зупинення бота
@flask_app.route('/stop_bot')
def stop_bot():
    global bot_active
    if bot_active:
        bot.stop()
        bot_active = False

    return "Bot stopped!"


@flask_app.route('/exit_control_panel')
def exit_control_panel():
    global bot_active
    if bot_active:
        bot.stop()
        bot_active = False
    print('Shutting down gracefully...')
    yield 'Server shutting down...'
    os.kill(os.getpid(), signal.SIGINT)


if __name__ == '__main__':
    flask_app.run(debug=True)
