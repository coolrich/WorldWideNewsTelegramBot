# from telebot import types
from bot_view import BotView
from user_storage import Users
from wwntgbotlib.country_codes import CountryCodes
from user_model import User
from navigation_menu import Navigator, Item, Action
import pickle
from google.cloud import storage

class BotModel:
    def __init__(self, a_logger, token):
        self.token = token
        self.logger = a_logger
        self.users_storage = Users()      
    
    
    
    def get_navigator(self, message):
        chat_id = message['chat']['id']
        navigation_users_data_bucket = storage.Client().bucket("navigation_users_data")
        blob = navigation_users_data_bucket.blob(f"user_{chat_id}_nav_data.pickle")
        if blob.exists():
            navigator_pkl = blob.download_as_string()
            navigator = pickle.loads(navigator_pkl)
            print(navigator)
            return navigator
        navigator = self.create_navigator()
        return navigator
    
    
    
    def save_navigator_state(self, navigator: Navigator, message):
        chat_id = message['chat']['id']
        print(navigator)
        # import sys
        # sys.exit(0)
        nav_attrs_pkl = pickle.dumps(navigator)
        navigation_users_data_bucket = storage.Client().bucket("navigation_users_data")
        blob = navigation_users_data_bucket.blob(f"user_{chat_id}_nav_data.pickle")
        blob.upload_from_string(nav_attrs_pkl)
    
    
    
    def create_navigator(self):
        class GetData(Action):
            def run(self, message):
                chat_id = message["chat"]["id"]
                parse_mode = 'MarkdownV2'
                message_text = message["text"]

                self.logger.debug(f"Message: {message_text}")
                user = self.get_user(chat_id)
                if user is None:
                    user = self.add_user(chat_id)
                news_article = self.get_news_article(message_text, user)
                post = BotView.get_post(news_article)
                self.save_user(user)
                return post
        
        main = Item("Головна")
        news = main.add_next_item("Новини")
        ukraine_news = news.add_next_item("України")
        last_ukraine_news = ukraine_news.add_next_item("Останні")
        past_ukraine_news = ukraine_news.add_next_item("Минулі")
        world_news = news.add_next_item("Світу")
        last_world_news = world_news.add_next_item("Last")
        past_world_news = world_news.add_next_item("Past")
        settings = main.add_next_item("Налаштування")
        get_data = GetData()
        last_ukraine_news.add_action(get_data)
        last_world_news.add_action(get_data)
        return Navigator(main, "Назад")
    
    def reset_navigator(self, message):
        navigator = self.create_navigator()
        self.save_navigator_state(navigator, message)
        return navigator
    
 
    

    @staticmethod
    def get_news_article(message_text, user: User):
        return user.get_news_article(CountryCodes.get_member_by_value(message_text))

    def get_user(self, chat_id):
        return self.users_storage.get_user(chat_id)

    def is_new_user(self, chat_id):
        # return chat_id not in self.users_storage.users
        return self.users_storage.get_user(chat_id) is None

    def save_user(self, user: User):
        self.users_storage.add_user(user)

    def add_user(self, chat_id):
        user = self.users_storage.add_user(User(chat_id))
        return user
