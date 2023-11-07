from typing import List

from country_codes.country_codes import CountryCodes
from news_handling.news_article import NewsArticle


class LoaderInterface:
    def load_news(self) -> (CountryCodes, List[NewsArticle]):
        pass
