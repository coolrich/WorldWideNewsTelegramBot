import logging
import time
from abc import ABC, abstractmethod
from typing import List, Any

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from country_codes.country_codes import CountryCodes
from news_handling.loader_interface import LoaderInterface
from news_handling.news_article import NewsArticle


class NewsScraperInterface(ABC, LoaderInterface):
    def __init__(self, a_logger: logging.Logger, address: str, country: CountryCodes):
        self.__address = address
        self.__logger = a_logger
        self.__country = country

    # Create properties for address
    @property
    def address(self):
        return self.__address

    # Create properties for country
    @property
    def country(self):
        return self.__country

    # def __get_html_source(self, url):
    #     self.__logger.debug("Start of __get_html_source")
    #     # time.sleep(3)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #     page_source = driver.execute_script('return document.documentElement.outerHTML')
    #     driver.quit()
    #     self.__logger.debug("End of __get_html_source")
    #     return page_source

    def __get_html_source(self, url):
        self.__logger.debug("Start of __get_html_source")

        response = requests.get(url)
        if response.status_code == 200:
            page_source = response.text
            self.__logger.debug("Successfully fetched HTML source")
        else:
            self.__logger.error("Failed to fetch HTML source: {}".format(response.status_code))
            page_source = None

        self.__logger.debug("End of __get_html_source")
        return page_source

    def __get_html_source_from_folder(self, absolute_file_path):
        self.__logger.debug("Start of __get_html_source_from_folder")
        with open(absolute_file_path, "r", encoding="UTF-8") as f:
            html_str = f.read()
        page_source = html_str
        self.__logger.debug(f"End of __get_html_source_from_folder: {absolute_file_path}")
        return page_source

    # add hints to method
    def __parse_news(self, base_url, html_source) -> List[NewsArticle]:
        self.__logger.debug(f"Start of parsing {html_source}")
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        try:
            news_list: list[NewsArticle] = self._parser(base_url, bs)
            return news_list
        except Exception as e:
            self.__logger.error(f"An unexpected error when parsing {base_url}: {e}")
        self.__logger.debug(f"End of parsing {html_source}")
        return []

    @abstractmethod
    def _parser(self, base_url: str, bs: BeautifulSoup) -> List[NewsArticle]:
        pass

    def load_news(self) -> (float, List[NewsArticle]):
        """
        Load news from a specified address.

        Returns:
            A tuple containing the Countries object and a list of News objects.
        """
        if self.address.startswith("http"):
            page = self.__get_html_source(self.address)
        else:
            page = self.__get_html_source_from_folder(self.address)
        news_list = self.__parse_news(self.address, page)
        timestamp = time.time()
        return timestamp, news_list
