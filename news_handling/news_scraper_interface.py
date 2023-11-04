import logging
import time
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from selenium import webdriver
from countries.countries import Countries

class NewsScraperInterface(ABC):
    def __init__(self, a_logger: logging.Logger, address: str, country: Countries):
        self._address = address
        self.logger = a_logger

    # Create properties for address
    @property
    def address(self):
        return self._address

    def __get_html_source(self, url):
        self.logger.debug("Start of __get_html_source")
        time.sleep(3)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.execute_script('return document.documentElement.outerHTML')
        driver.quit()
        self.logger.debug("End of __get_html_source")
        return page_source

    def __get_html_source_from_folder(self, absolute_file_path):
        self.logger.debug("Start of __get_html_source_from_folder")
        with open(absolute_file_path, "r", encoding="UTF-8") as f:
            html_str = f.read()
        page_source = html_str
        self.logger.debug(f"End of __get_html_source_from_folder: {absolute_file_path}")
        return page_source

    # add hints to method
    def _parse_news(self, base_url, html_source):
        self.logger.debug(f"Start of parsing {html_source}")
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        try:
            posts_dict = self._parser(base_url, bs)
            return posts_dict
        except Exception as e:
            self.logger.error(f"An unexpected error when parsing {base_url}: {e}")
        self.logger.debug(f"End of parsing {html_source}")
        return None

    @abstractmethod
    def _parser(self, base_url: str, bs: BeautifulSoup) -> dict:
        pass

    def load_news(self):
        # check if self.address is URL use get_html_source else use get_html_source_from_folder
        if self.address.startswith("http"):
            bbc_page = self.__get_html_source(self.address)
        else:
            bbc_page = self.__get_html_source_from_folder(self.address)
        news_dict = self._parse_news(self.address, bbc_page)
        return news_dict


