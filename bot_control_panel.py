from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_login import login_required, login_user, UserMixin, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from controllers.application_controller import ApplicationController

# Змінна-флаг для вказування на стан бота (активний або призупинений)
bot_active = False

# Створіть веб-сервер Flask
bot = ApplicationController(is_debug_mode=True)
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure random key
Bootstrap(flask_app)
login_manager = LoginManager()
login_manager.init_app(flask_app)

# Replace this with a database (e.g., SQLAlchemy) for production use.
__users = [{'username': 'admin', 'password': generate_password_hash('admin')}]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class User(UserMixin):
    __user_counter = 0
    __users = {}

    def __init__(self):
        self.id = str(User.__user_counter)
        User.__user_counter = str(int(User.__user_counter) + 1)
        User.__users[self.id] = self

    @staticmethod
    def get(user_id):
        return User.__users.get(user_id, None)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@flask_app.route('/', methods=['GET', 'POST'])
def login_control_panel():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = next((user for user in __users if user['username'] == username), None)
        if user and check_password_hash(user['password'], password):
            # Successful login
            user_obj = User()
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


# Обробник головної сторінки

@flask_app.route('/index')
@login_required
def index():
    return render_template('index.html')


# Обробник для команди запуску бота
@flask_app.route('/start_bot')
@login_required
def start_bot():
    global bot_active
    if not bot_active:
        bot.start()
        bot_active = True

    return render_template('index.html', message="Bot started.")


# Обробник для команди зупинення бота
@flask_app.route('/stop_bot')
@login_required
def stop_bot():
    global bot_active
    if bot_active:
        bot.stop()
        bot_active = False

    return render_template('index.html', message="Bot stopped.")


@flask_app.route('/logout')
@login_required
def logout_control_panel():
    global bot_active
    if bot_active:
        bot.stop()
        bot_active = False
    logout_user()
    # return redirect(url_for('login_control_panel'))
    return render_template("intermediate_logout_page.html")


if __name__ == '__main__':
    flask_app.run(debug=True)
