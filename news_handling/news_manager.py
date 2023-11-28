import pickle

import google.cloud.storage
from google.cloud import storage
from google.cloud.exceptions import NotFound

from country_codes.country_codes import CountryCodes
from news_handling.news_article import NewsArticle
from news_handling.news_scrapers import UANewsScraper, WorldNewsScraper


class NewsManager:
    bucket_name: str = "my_news_bucket"
    client = storage.Client()

    def __init__(self,
                 a_logger):
        self.__scrapers = [WorldNewsScraper(a_logger), UANewsScraper(a_logger)]
        self.__logger = a_logger

    @staticmethod
    def get_filename(country_code: CountryCodes):
        return f"{country_code.name}-news.pkl"

    def get_news(self):
        for scraper in self.__scrapers:
            self.__logger.debug("In task get_news")
            filename = NewsManager.get_filename(scraper.country_code)
            self.__logger.info(f"Loading {scraper.country_code} news from {scraper.address}...")
            timestamp, news_list = scraper.load_news()
            NewsManager.save_to_gcs_bucket(filename, timestamp, news_list, scraper.country_code)
            self.__logger.info(f"News has been saved to {filename} on GCS!")
            self.__logger.info(f"Number of {scraper.country_code} news: {len(news_list)}")
            self.__logger.debug(f"End of task {scraper.address}")

    @staticmethod
    def save_to_gcs_bucket(filename, timestamp: float, news_list: list[NewsArticle], country_code: CountryCodes) \
            -> None:
        """
        Save the given news articles data to a Google Cloud Storage bucket.

        Parameters:
            filename (str): The name of the file to be saved.
            timestamp (float): The timestamp of when the news articles data was generated.
            news_list (list[NewsArticle]): A list of NewsArticle objects containing the news articles data.
            country_code (CountryCodes): The country code associated with the news articles data.

        Returns:
            None
        """
        bucket_name = NewsManager.bucket_name
        bucket = NewsManager.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        data = pickle.dumps((timestamp, news_list, country_code))
        blob.upload_from_string(data)

    @staticmethod
    def load_from_gcs_bucket(filename) -> (float, list[NewsArticle]):
        """
        A static method that loads data from a Google Cloud Storage (GCS) bucket.

        Args:
            filename (str): The name of the file to load from the GCS bucket.

        Returns:
            tuple: A tuple containing the timestamp (float) and a list of NewsArticle objects.

        Raises:
            NotFound: If the specified file is not found in the GCS bucket.
        """
        timestamp, news_list = None, None
        bucket_name = NewsManager.bucket_name
        bucket: google.cloud.storage.bucket.Bucket = NewsManager.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        try:
            data_string = blob.download_as_string()
        except NotFound:
            return timestamp, news_list
        data = pickle.loads(data_string)
        timestamp, news_list = data
        return timestamp, news_list

    @staticmethod
    def get_articles_list_from_gcs_bucket() -> list:
        """
        Loads all files from a Google Cloud Storage (GCS) bucket and returns a list of articles.

        This static method takes no parameters and returns a list of articles. It assumes that the
        bucket name is stored in the `bucket_name` attribute of the `NewsManager` class.

        Returns:
            list: A list of articles, where each article is a deserialized object obtained from
            the files in the GCS bucket. Each element is a tuple of (timestamp, news_list, country_code).

        Raises:
            NotFound: If a file in the GCS bucket is not found or cannot be downloaded.

        """
        bucket_name = NewsManager.bucket_name
        bucket: google.cloud.storage.bucket.Bucket = NewsManager.client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        articles_list = []
        for blob in blobs:
            try:
                data_string = blob.download_as_string()
            except NotFound:
                continue
            data = pickle.loads(data_string)
            articles_list.append(data)
        return articles_list

    @staticmethod
    def get_timestamp_and_news_articles_list(country_code: CountryCodes) -> (float, list[NewsArticle]):
        filename = NewsManager.get_filename(country_code)
        timestamp, news_list = NewsManager.load_from_gcs_bucket(filename)
        return timestamp, news_list


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    news_manager = NewsManager(logging.getLogger())
    news_manager.get_news()
