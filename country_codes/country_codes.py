from enum import Enum
import logging


class CountryCodes(Enum):
    # logger: logging.Logger = logging.getLogger()
    UA = ['Новини України']
    WORLD = ['Новини Світу']

    def __eq__(self, text):
        if isinstance(text, str):
            for country in CountryCodes:
                # print("Country: ", country, "Text: ", text)
                if text in country.value:
                    print("Country: ", country, "\nText: ", text)
                    return True
            return False


if __name__ == '__main__':
    print(CountryCodes.UA == 'Новини України')
    print(CountryCodes.WORLD == 'Новини Світу')
    # Some invalid test
    print(CountryCodes.UA == 'Новини')
