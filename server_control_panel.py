from flask import Flask, render_template
import main
import threading

# Отримайте токен бота від BotFather
bot_token = 'YOUR_BOT_TOKEN'

# Створіть екземпляр бота
bot = telebot.TeleBot(bot_token)

# Змінна-флаг для вказування на стан бота (активний або призупинений)
bot_active = True
bot_thread = None

# Створіть веб-сервер Flask
app = Flask(__name__)

# Обробник головної сторінки
@app.route('/')
def index():
   return render_template('index.html')

# Обробник для команди запуску бота
@app.route('/start_bot')
def start_bot():
   global bot_active
   global bot_thread

   if not bot_active:
       bot_thread = threading.Thread(target=bot.polling)
       bot_thread.start()
       bot_active = True

   return "Bot started!"

# Обробник для команди призупинення бота
@app.route('/pause_bot')
def pause_bot():
   global bot_active
   global bot_thread

   if bot_active:
       if bot_thread:
           bot_thread.join()
           bot_thread = None
       bot_active = False

   return "Bot paused!"

# Обробник для команди зупинення бота
@app.route('/stop_bot')
def stop_bot():
   global bot_active
   global bot_thread

   if bot_active:
       if bot_thread:
           bot_thread.join()
           bot_thread = None
       bot_active = False
       bot.stop_polling()

   return "Bot stopped!"

# Додайте інші обробники за потребою

if __name__ == '__main__':
   app.run(debug=True)
