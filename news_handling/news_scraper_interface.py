import time
from abc import ABC, abstractmethod

from selenium import webdriver


class NewsScraperInterface(ABC):
    def __init__(self, a_logger):
        self.logger = a_logger

    def get_html_source(self, url):
        self.logger.debug("Start of get_html_source")
        time.sleep(3)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.execute_script('return document.documentElement.outerHTML')
        driver.quit()
        self.logger.debug("End of get_html_source")
        return page_source

    def _get_html_source_from_folder(self, absolute_file_path):
        self.logger.debug("Start of get_bbc_news_source_from_folder")
        with open(absolute_file_path, "r", encoding="UTF-8") as f:
            html_str = f.read()
        page_source = html_str
        self.logger.debug(f"End of _get_news_source_from_folder: {absolute_file_path}")
        return page_source

    @abstractmethod
    def _parse_news(self, base_url, html_source):
        pass

    @abstractmethod
    def get_news(self):
        pass

    @abstractmethod
    def get_test_news(self):
        pass