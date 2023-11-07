from enum import Enum
import logging

from news_handling.news_article import NewsArticle


class CountryCodes(Enum):
    # logger: logging.Logger = logging.getLogger()
    UA = ['Новини України']
    WORLD = ['Новини Світу']

    def __eq__(self, text):
        if isinstance(text, str):
            for country_code in CountryCodes:
                print("Country: ", country_code, "Text: ", text)
                if text in country_code.value:
                    print("Country: ", country_code, "\nText: ", text)
                    return True
            return False

    def __hash__(self):
        return hash(tuple(self.value))


if __name__ == '__main__':
    # print(CountryCodes.UA == 'Новини України')
    # print(CountryCodes.WORLD == 'Новини Світу')
    # # Some invalid test
    # print(CountryCodes.UA == 'Новини')
    # create an example of a dict with values {country_code_1 : NewsList_1, country_code_2: NewsList_2}
    a_dict = {CountryCodes.UA: [NewsArticle("News about UA", "Some news", "https://www.google.com", 1)],
              CountryCodes.WORLD: [NewsArticle("News ", "about UA_1", "News text", 1)]}
    print(a_dict["Новини України"])
