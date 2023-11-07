
class NewsArticle:
    """
    Initializes a new instance of the class.

    Args:
        title (str): The title of the object.
        text (str): The text of the object.
        url (str): The URL of the object.
        timestamp (int): The timestamp of the object.
    """
    def __init__(self, title: str, text: str, url: str, timestamp: float):
        self.__title = title
        self.__text = text
        self.__url = url
        self.__timestamp = timestamp

    @property
    def get_title(self):
        return self.__title

    @property
    def get_text(self):
        return self.__text

    @property
    def get_url(self):
        return self.__url

    @property
    def get_timestamp(self):
        return self.__timestamp

    def get_summary(self, max_length=100):
        # Return a summary of the article text, truncated to max_length characters
        return self.__text[:max_length]

    def __str__(self):
        # Customize the string representation of the NewsArticle for easy printing
        return f"Title: {self.__title}\nURL: {self.__url}\nTimestamp: {self.__timestamp}"