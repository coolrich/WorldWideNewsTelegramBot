import textwrap
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from news_handling.news_scraper_interface import NewsScraperInterface


class UANewsScraper(NewsScraperInterface):
    def __init__(self, a_logger, ua_url=r"https://www.bbc.com/ukrainian"):
        super().__init__(a_logger)
        self.ua_url = ua_url

    def _parse_news(self, base_url, html_source):
        self.logger.debug("Start of parse_bbc_ukraine")
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        posts_dict = {}
        try:
            section_tags = bs.find('main').find_all('section')
            for section in section_tags:
                try:
                    h3_tag = section.h3
                    if h3_tag:
                        heading = h3_tag.text.replace('\n', ' ').title()
                        href_link = h3_tag.a['href']
                        full_url = urljoin(base_url.rstrip('/') + '/', href_link.lstrip('/'))
                        text = textwrap.fill(h3_tag.next_sibling.text.replace('\n', ''), 50)
                        self.logger.debug(f"Heading: {heading}")
                        self.logger.debug(f"Url: {full_url}")
                        self.logger.debug(f"Text: {text}\n")
                        posts_dict[heading] = [text, full_url]
                except AttributeError as e:
                    self.logger.error(f"AttributeError in bbc-ukraine parser: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"An unexpected error in bbc-ukraine occurred: {e}")
        self.logger.debug("End of parse_bbc_ukraine")
        return posts_dict

    def get_news(self):
        bbc_page = self.get_html_source(self.ua_url)
        news_dict = self._parse_news(self.ua_url, bbc_page)
        return news_dict

    def get_test_news(self):
        bbc_page = self._get_html_source_from_folder("test_sources/bbc-news-ukraine.html")
        news_dict = self._parse_news(self.ua_url, bbc_page)
        return news_dict


class WorldNewsScraper(NewsScraperInterface):
    def __init__(self, a_logger, world_url=r"https://www.bbc.com/news"):
        super().__init__(a_logger)
        self.world_url = world_url
        self.logger = a_logger

    def _parse_news(self, base_url, html_source):
        self.logger.debug("Start of parse_bbc")
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        posts = bs.find('div', {'id': 'latest-stories-tab-container'}).find_all('div', 'gs-c-promo')
        posts_dict = {}
        try:
            for post in posts:
                try:
                    heading = post.find('a').find('h3').text
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
                    posts_dict[heading] = [text, full_url]
                except AttributeError as e:
                    self.logger.error(f"AttributeError in bbc parser: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"An unexpected error in bbc-parser occurred: {e}")
            # sys.exit()
        self.logger.debug("End of parse_bbc")
        return posts_dict

    def get_news(self):
        bbc_page = self.get_html_source(self.world_url)
        news_dict = self._parse_news(self.world_url, bbc_page)
        return news_dict

    def get_test_news(self):
        bbc_page = self._get_html_source_from_folder("test_sources/bbc-news.html")
        news_dict = self._parse_news(self.world_url, bbc_page)
        return news_dict


if __name__ == '__main__':
    import logging

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
    # world_news = ns.get_world_news()
    ua_news = ns.get_news()
    # logger.debug("World news:")
    # logger.debug(f"Count of world news: {len(world_news)}")
    logger.debug("UA news:")
    logger.debug(f"Count of UA news: {len(ua_news)}")
    logger.debug("End of the __main__() method in NewsScraper class")
