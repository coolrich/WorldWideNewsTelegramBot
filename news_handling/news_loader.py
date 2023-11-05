import json
import logging
import time
from typing import List

from countries.countries import Countries
from news_handling.loader_interface import LoaderInterface
from news_handling.news import News


class NewsFileLoader(LoaderInterface):
    def __init__(self, logger: logging.Logger, news_file_path, timestamp_file_path):
        self.news_file_path = news_file_path
        self.timestamp_file_path = timestamp_file_path
        self.logger = logger

    def save_news_and_timestamp_in_seconds(self, country: Countries, news_list: List[News]):
        with open(self.news_file_path, "w") as json_file:
            json.dump({country: news_list}, json_file)

        # Save the timestamp to a separate file
        timestamp = int(time.time())  # Current Unix timestamp
        with open(self.timestamp_file_path, "w") as timestamp_file:
            timestamp_file.write(str(timestamp))

    def load_news(self) -> (Countries, List[News]):
        try:
            with open(self.news_file_path, "r") as json_file:
                news_data = json.load(json_file)
            return news_data
        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.error("News file not found")
            return []

    def get_last_download_timestamp_in_seconds(self):
        try:
            with open(self.timestamp_file_path, "r") as timestamp_file:
                timestamp = int(timestamp_file.read())
            return timestamp
        except (FileNotFoundError, ValueError):
            self.logger.error("Timestamp file not found")
            return None
