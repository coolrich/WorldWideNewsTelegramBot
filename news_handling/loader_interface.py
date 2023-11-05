from typing import List

from countries.countries import Countries
from news_handling.news import News


class LoaderInterface:
    def load_news(self) -> (Countries, List[News]):
        pass
