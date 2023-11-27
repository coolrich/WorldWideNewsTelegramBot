import pickle
import threading
import time

import google.cloud.storage
from google.cloud import storage
from google.cloud.exceptions import NotFound

from controllers.program_state_controller import program_state_controller as psc
from news_handling.news_article import NewsArticle
from news_handling.news_scrapers import UANewsScraper, WorldNewsScraper
from news_handling.runtime_news_storage import RuntimeNewsStorage


class NewsManager:
    def __init__(self,
                 condition_lock: threading.Condition,
                 a_logger,
                 news_update_period: int = 60):
        self.bucket_name = "my_news_bucket"
        self.client = storage.Client()
        self.__scrapers = [WorldNewsScraper(a_logger), UANewsScraper(a_logger)]
        self.__lock = condition_lock
        self.__logger = a_logger
        self.__runtime_news_storage = RuntimeNewsStorage()
        self.__news_update_period = news_update_period

    def get_runtime_news_storage(self):
        return self.__runtime_news_storage

    def get_news(self):
        while psc.get_program_state():
            psc.set_news_state(False)
            with self.__lock:
                for scraper in self.__scrapers:
                    self.__logger.debug("In task get_news")

                    country_code = scraper.country
                    filename = f"{country_code.name}-news.pkl"

                    # load from file
                    # timestamp, news_list = self.load_news(filename)

                    # load from GCS cache
                    timestamp, news_list = self.load_from_cache(filename)

                    if news_list is not None:
                        self.__logger.info(f"News \"{filename}\" has been loaded from cache GCS bucket!")

                    self.__logger.info(f"Loading {country_code} news...")
                    self.__logger.debug(f"Loading data from {filename}...")
                    self.__logger.debug(f"news list: {news_list}, timestamp: {timestamp}")

                    if news_list is None or news_list == [] or self.is_news_outdated(timestamp):
                        self.__logger.info(f"Loading {country_code} news from {scraper.address}...")
                        timestamp, news_list = scraper.load_news()
                        # save to file
                        # NewsManager.save_news(filename, timestamp, news_list)
                        # save to GCS cache
                        self.save_to_cache(filename, timestamp, news_list)
                        self.__logger.info(f"News has been saved to {filename}!")

                    # Number of news articles of country
                    self.__logger.info(f"Number of {country_code} news: {len(news_list)}")

                    self.__runtime_news_storage.add_news(country_code, timestamp, news_list)
                    self.__logger.debug(f"End of task {scraper.address}")
                self.__waiting()

    def __waiting(self):
        while not self.is_news_outdated() and psc.get_program_state():
            psc.set_news_state(True)
            self.__logger.debug(f"Sleeping in get_news on {self.__news_update_period}...")
            self.__lock.notify_all()
            self.__lock.wait(self.__news_update_period)
        self.__runtime_news_storage.reset_last_timestamp()

    def is_news_outdated(self, timestamp: float = None):
        if timestamp is None:
            t0 = self.__runtime_news_storage.get_last_timestamp()
        else:
            t0 = timestamp
        return time.time() - t0 > self.__news_update_period

    @staticmethod
    def save_news(filename, timestamp: float, news_list: list[NewsArticle]):
        news_tuple = (timestamp, news_list)
        with open(filename, "wb") as file:
            pickle.dump(news_tuple, file)

    def save_to_cache(self, filename, timestamp: float, news_list: list[NewsArticle]):
        # Set the Google Cloud Storage bucket name
        # bucket_name = os.environ.get('GCS_BUCKET_NAME')

        bucket_name = self.bucket_name

        # Create a bucket object
        bucket = self.client.bucket(bucket_name)

        # Create a blob object with the unix timestamp as the filename
        blob = bucket.blob(filename)

        # Serialize the news articles data using pickle
        data = pickle.dumps((timestamp, news_list))

        # Upload the data to the blob
        blob.upload_from_string(data)

    def load_news(self, filename) -> (float, list[NewsArticle]):
        try:
            with open(filename, "rb") as file:
                timestamp, news_list = pickle.load(file)
                return timestamp, news_list
        except FileNotFoundError:
            self.__logger.debug(f"File {filename} not found.")
        return None, None

    def load_from_cache(self, filename) -> (float, list[NewsArticle]):
        # Set the Google Cloud Storage bucket name
        # bucket_name = os.environ.get('GCS_BUCKET_NAME')
        timestamp, news_list = None, None
        bucket_name = self.bucket_name

        # Create a bucket object with annotation of the type
        bucket: google.cloud.storage.bucket.Bucket = self.client.bucket(bucket_name)

        # Download the blob as a string
        blob = bucket.blob(filename)
        try:
            data_string = blob.download_as_string()
        except NotFound:
            return timestamp, news_list
        # Deserialize the data using pickle
        data = pickle.loads(data_string)
        timestamp, news_list = data

        return timestamp, news_list


if __name__ == "__main__":
    import logging
    import threading

    logging.basicConfig(level=logging.DEBUG)
    news_manager = NewsManager(threading.Condition(), logging.getLogger(), 60 * 2)
    news_manager.get_news()
