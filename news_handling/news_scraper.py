import textwrap
from urllib.parse import urljoin
import logging
from news_handling.news_scraper_interface import NewsScraperInterface


class UANewsScraper(NewsScraperInterface):
    def __init__(self, a_logger: logging.Logger, an_address: str = r"https://www.bbc.com/ukrainian"):
        super().__init__(a_logger, an_address)

    def _parser(self, base_url, bs):
        posts_dict = {}
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
        return posts_dict


class WorldNewsScraper(NewsScraperInterface):
    def __init__(self, a_logger: logging.Logger, an_address: str = r"https://www.bbc.com/news"):
        super().__init__(a_logger, an_address)
        self.logger = a_logger

    def _parser(self, base_url, bs):
        posts_dict = {}
        posts = bs.find('div', {'id': 'latest-stories-tab-container'}).find_all('div', 'gs-c-promo')
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
        self.logger.debug("End of parse_bbc")
        return posts_dict


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
