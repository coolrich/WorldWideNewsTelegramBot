from bot_view import BotView
from user_storage import Users
from wwntgbotlib.country_codes import CountryCodes
from user_model import User
from navigation_menu import Navigator, Item, Action
import pickle
from google.cloud import storage

class DataController(Action):
    def __init__(self, a_logger, token):
        self.token = token
        self.users_storage = Users()      
        self.logger = a_logger
    
    def run(self, message):
        print("Start get data")
        chat_id = message["chat"]["id"]
        parse_mode = 'MarkdownV2'
        message_text = message["text"]

        self.logger.debug(f"Message: {message_text}")
        user = self.__get_user(chat_id)
        if user is None:
            user = self.__add_user(chat_id)
        news_article = DataController.__get_news_article(message_text, user)
        post = BotView.get_post(news_article)
        self.__save_user(user)
        print("Finish get data")
        return post   
    
    @staticmethod
    def __get_news_article(message_text, user: User):
        return user.get_news_article(CountryCodes.get_member_by_value(message_text))

    def __get_user(self, chat_id):
        return self.users_storage.get_user(chat_id)

    def __save_user(self, user: User):
        self.users_storage.add_user(user)

    def __add_user(self, chat_id):
        user = self.users_storage.add_user(User(chat_id))
        return user
    
    def __getstate__(self):
        return {
        "token" : self.token,
        "users_storage" : self.users_storage,
        "logger" : self.logger
        }

    def __setstate__(self, state):
        self.token = state["token"]
        self.users_storage = state["users_storage"]
        self.logger = state["logger"]
    
class MyTestClass(Action):
    def run(self, message):
        print("Hello from MyTestClass!!!!!!!!!!!!!!!!!!")

class NavigatorController:
    def __init__(self, data_controller):
        self.__data_controller = data_controller
    
    def create_navigator(self):    
        main = Item("Головна")
        news = main.add_next_item("Новини")
        ukraine_news = news.add_next_item("України")
        ukraine_news.add_action(self.__data_controller)
        world_news = news.add_next_item("Світу")
        last_world_news = world_news.add_next_item("Last")
        past_world_news = world_news.add_next_item("Past")
        settings = main.add_next_item("Налаштування")
        return Navigator(main, "Назад")
    
    def reset(self, message):
        navigator = self.create_navigator()
        self.save_state(navigator, message)
        return navigator
        
    def save_state(self, navigator: Navigator, message):
        chat_id = message['chat']['id']
        nav_pkl = pickle.dumps(navigator)
        navigation_users_data_bucket = storage.Client().bucket("navigation_users_data")
        blob = navigation_users_data_bucket.blob(f"user_{chat_id}_nav_data.pickle")
        blob.upload_from_string(nav_pkl)
        
    def get_navigator(self, message):
        chat_id = message['chat']['id']
        navigation_users_data_bucket = storage.Client().bucket("navigation_users_data")
        blob = navigation_users_data_bucket.blob(f"user_{chat_id}_nav_data.pickle")
        if blob.exists():
            navigator_pkl = blob.download_as_string()
            navigator = pickle.loads(navigator_pkl)
            return navigator
        navigator = self.create_navigator()
        return navigator
    
    