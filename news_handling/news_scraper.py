import pprint
import sys
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class NewsScraper:
    def __init__(self, ua_url=r"https://www.bbc.com/ukrainian", world_url=r"https://www.bbc.com/news"):
        self.ua_url = ua_url
        self.world_url = world_url

    @staticmethod
    def get_bbc_news_source_from_folder():
        with open("test_sources/bbc-news.html", "r", encoding="UTF-8") as f:
            html_str = f.read()
        page_source = html_str
        return page_source

    @staticmethod
    def get_bbc_news_ukraine_source_from_folder():
        try:
            with open("test_sources/bbc-news-ukraine.html", "r", encoding="utf-8") as f:
                html_str = f.read()
            page_source = html_str
            return page_source
        except FileNotFoundError:
            print("File not found. Make sure the file 'bbc-news-ukraine.html' exists in the 'test_sources' folder.")
        except UnicodeDecodeError:
            print("Error decoding the file. Ensure that the file is encoded in UTF-8.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        sys.exit()

    @staticmethod
    def get_html_source(url):
        time.sleep(3)
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.execute_script('return document.documentElement.outerHTML')
        driver.quit()
        return page_source

    def parse_bbc(self, base_url, html_source):
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        try:
            posts = bs.find('div', {'id': 'latest-stories-tab-container'}).find_all('div', 'gs-c-promo')
            posts_dict = {}
            for post in posts:
                heading = post.find('a').find('h3').text
                p_tag = post.find('p')
                if p_tag:
                    text = p_tag.get_text()
                else:
                    continue
                rel_link = post.find('a')['href']
                full_url = urljoin(base_url.rstrip('/') + '/', rel_link.lstrip('/'))
                print("Heading: " + heading + '\n')
                print("Url: " + full_url + '\n')
                print("Text: " + text)
                article_delimiter = len(heading) * '-'
                print(article_delimiter)
                posts_dict[heading] = [text, full_url]
        except Exception as e:
            print(f"An unexpected error in bbc-parser occurred: {e}")
            sys.exit()
        return posts_dict

    def parse_bbc_ukraine(self, base_url, html_source):
        base_url = base_url.split('.com')[0] + '.com'
        bs = BeautifulSoup(html_source, 'html5lib')
        try:
            section_tags = bs.find('main').find_all('section')
            print(section_tags[0])
            # sys.exit()
            posts_dict = {}
            import textwrap
            for section in section_tags:
                try:
                    h3_tag = section.h3
                    if h3_tag:
                        heading = h3_tag.text.replace('\n', ' ').title() + '\n'
                        print("Заголовок: " + heading)

                        href_link = h3_tag.a['href']
                        full_url = urljoin(base_url.rstrip('/') + '/', href_link.lstrip('/'))
                        print("Url: " + full_url + '\n')

                        text = textwrap.fill(h3_tag.next_sibling.text.replace('\n', ''), 50)
                        print("Текст_статті: " + text)

                        article_delimiter = len(heading) * '-'
                        print(article_delimiter)

                        posts_dict[heading] = [text, full_url]
                except AttributeError as e:
                    print(f"AttributeError in bbc parser: {e}")
                    continue
        except Exception as e:
            print(f"An unexpected error in bbc-parser occurred: {e}")
            sys.exit()
        return posts_dict

    def get_ua_news(self):
        bbc_page = self.get_html_source(self.ua_url)
        news_dict = self.parse_bbc_ukraine(self.ua_url, bbc_page)
        return news_dict

    def get_world_news(self):
        bbc_page = self.get_html_source(self.world_url)
        news_dict = self.parse_bbc(self.world_url, bbc_page)
        return news_dict

    def get_test_ua_news(self):
        bbc_page = self.get_bbc_news_ukraine_source_from_folder()
        news_dict = self.parse_bbc_ukraine(self.ua_url, bbc_page)
        return news_dict

    def get_test_world_news(self):
        bbc_page = self.get_bbc_news_source_from_folder()
        news_dict = self.parse_bbc(self.world_url, bbc_page)
        return news_dict


if __name__ == '__main__':
    ns = NewsScraper()
    # world_news = ns.get_world_news()
    ua_news = ns.get_ua_news()
    # print("World news:")
    # pprint.pprint(f"Count of world news: {len(world_news)}")
    print("UA news:")
    pprint.pprint(f"Count of UA news: {len(ua_news)}")
