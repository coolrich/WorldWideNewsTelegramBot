from enum import Enum
import logging
from news_handling.news_article import NewsArticle

logger: logging.Logger = logging.getLogger(__name__)

from core.keyboard_button_names import KeyboardButtonsNames as kbn


class CountryCodes(Enum):
    UA = [kbn.UA.value, ]
    WORLD = [kbn.WORLD.value, ]

    @staticmethod
    def get_member_by_value(item):
        logger.debug("In CountryCodes in method get_member_by_value")
        if isinstance(item, str):
            logger.debug("In CountryCodes in method get_member_by_value: " + str(item))
            for country_code in CountryCodes:
                # logger.debug("In CountryCodes: " + str(item))
                if str(item) in country_code.value:
                    logger.debug("In CountryCodes return value: " + str(country_code))
                    return country_code
        raise KeyError

    # def __call__(self, *args, **kwargs):
    #     CountryCodes.get_member_by_value(args[0])


if __name__ == '__main__':
    # print(CountryCodes.UA == 'Новини України')
    # print(CountryCodes.WORLD == 'Новини Світу')
    # # Some invalid test
    # print(CountryCodes.UA == 'Новини')
    # create an example of a dict with values {country_code_1 : NewsList_1, country_code_2: NewsList_2}
    a_dict = CountryCodes({CountryCodes.UA: [NewsArticle("News about UA", "Some news", "https://www.google.com", 1)],
                           CountryCodes.WORLD: [NewsArticle("News ", "about UA_1", "News text", 1)]})
