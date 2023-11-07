import textwrap
import time
from urllib.parse import urljoin
import logging

from country_codes.country_codes import CountryCodes
from news_handling.newsarticle import NewsArticle
from news_handling.news_scraper_interface import NewsScraperInterface


class UANewsScraper(NewsScraperInterface):
    def __init__(self, a_logger: logging.Logger, an_address: str = r"https://www.bbc.com/ukrainian"):
        super().__init__(a_logger, an_address, CountryCodes.UA)
        self.logger = a_logger

    def _parser(self, base_url, bs):
        news_list = []
        section_tags = bs.find('main').find_all('section')
        for section in section_tags:
            try:
                h3_tag = section.h3
                if h3_tag:
                    heading = h3_tag.__text.replace('\n', ' ').__title()
                    href_link = h3_tag.a['href']
                    full_url = urljoin(base_url.rstrip('/') + '/', href_link.lstrip('/'))
                    text = textwrap.fill(h3_tag.next_sibling.__text.replace('\n', ''), 50)
                    self.logger.debug(f"Heading: {heading}")
                    self.logger.debug(f"Url: {full_url}")
                    self.logger.debug(f"Text: {text}\n")
                    news_list.append(NewsArticle(heading, text, full_url, time.time()))
            except AttributeError as e:
                self.logger.error(f"AttributeError in bbc-ukraine parser: {e}")
                continue
        self.logger.debug("End of parse_bbc_ukraine")
        return news_list


class WorldNewsScraper(NewsScraperInterface):
    def __init__(self, a_logger: logging.Logger, an_address: str = r"https://www.bbc.com/news"):
        super().__init__(a_logger, an_address, CountryCodes.WORLD)
        self.logger = a_logger

    def _parser(self, base_url, bs):
        news_list = []
        posts = bs.find('div', {'id': 'latest-stories-tab-container'}).find_all('div', 'gs-c-promo')
        for post in posts:
            try:
                heading = post.find('a').find('h3').__text
                p_tag = post.find('p')
                if p_tag:
                    text = p_tag.get_text()
                else:
                    continue
                rel_link = post.find('a')['href']
                full_url = urljoin(base_url.rstrip('/') + '/', rel_link.lstrip('/'))
                self.logger.debug(f"Heading: {heading}")
                self.logger.debug(f"Url: {full_url}")
                self.logger.debug(f"Text: {text}")
                news_list.append(NewsArticle(heading, text, full_url, time.time()))
            except AttributeError as e:
                self.logger.error(f"AttributeError in bbc parser: {e}")
                continue
        self.logger.debug("End of parse_bbc")
        return news_list


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    logger = logging.getLogger()
    logger.debug("Start of the __main__() method in NewsScraper class")
    ns = UANewsScraper(a_logger=logger)
    ua_news = ns.load_news()
    logger.debug("UA news:")
    logger.debug(f"Count of UA news: {len(ua_news)}")
    logger.debug("End of the __main__() method in NewsScraper class")
