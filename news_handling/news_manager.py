import threading

from news_handling.news_scraper import NewsScraper
from bot_mvc import BotController
import time


class NewsManager:
    def __init__(self, condition_lock: threading.Condition, program_state_controller):
        self.scraper = NewsScraper()
        self.lock = condition_lock
        self.program_state_controller = program_state_controller

    def get_world_news(self, a_bot_controller: BotController, delay: int = 60):
        get_program_state = self.program_state_controller.get_state
        while get_program_state():
            with self.lock:
                print("In get_world_news")
                a_bot_controller.bot_model.world_news_dict = self.scraper.get_test_world_news()
                print("-" * 50)
                print(f"Count of World news: {len(a_bot_controller.bot_model.world_news_dict)}")
                print("-" * 50)
                print(f"Sleeping in get_world_news on {delay}...")
                self.lock.wait(delay)
        self.lock.notify_all()
        print("End of get_world_news")
            # time.sleep(delay)

    def get_ua_news(self, a_bot_controller: BotController, delay: int = 60):
        get_program_state = self.program_state_controller.get_state
        while get_program_state():
            with self.lock:
                print("In get_ua_news")
                a_bot_controller.bot_model.ua_news_dict = self.scraper.get_test_ua_news()
                print("-" * 50)
                print(f"Count of UA news: {len(a_bot_controller.bot_model.ua_news_dict)}")
                print("-" * 50)
                print(f"Sleeping in get_ua_news on {delay}...")
                self.lock.wait(delay)
        self.lock.notify_all()
        print("End of get_ua_news")
            # time.sleep(delay)
