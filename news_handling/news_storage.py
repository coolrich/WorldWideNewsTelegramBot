import json


class NewsStorage:
    def __init__(self, file_path):
        self.file_path = file_path

    def save_news(self, news_data):
        with open(self.file_path, "w") as json_file:
            json.dump(news_data, json_file)

    def load_news(self):
        try:
            with open(self.file_path, "r") as json_file:
                news_data = json.load(json_file)
            return news_data
        except FileNotFoundError:
            # Handle the case where the file doesn't exist or is empty
            return []
