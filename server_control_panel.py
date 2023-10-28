import os
import signal

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.application_controller import ApplicationController

# TODO: Add authorization with login and password

# Змінна-флаг для вказування на стан бота (активний або призупинений)
bot_active = False

# Створіть веб-сервер Flask
bot = ApplicationController()
flask_app = Flask(__name__)

flask_app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure random key

# Replace this with a database (e.g., SQLAlchemy) for production use.
users = [{'username': 'admin', 'password': generate_password_hash('adminpassword')}]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@flask_app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = next((user for user in users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            # Successful login
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


# Обробник головної сторінки
@flask_app.route('/index')
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
