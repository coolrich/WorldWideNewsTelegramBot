import pprint
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_html_source_from_folder():
    with open("bbc_news.html", "r") as f:
        html_str = f.read()
    page_source = html_str
    return page_source


def get_html_source(url):
    time.sleep(3)
    driver = webdriver.Chrome()
    driver.get(url)
    page_source = driver.execute_script('return document.documentElement.outerHTML')
    driver.quit()
    return page_source


def parse_page(base_url, html_source):
    base_url = base_url.split('.com')[0] + '.com'
    bs = BeautifulSoup(html_source, 'html5lib')
    posts = bs.find_all('div', {'class': 'gs-c-promo-body'})
    # print(posts)
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
        posts_dict[heading] = [text, full_url]
        # print(posts_dict)
    return posts_dict


def get_news():
    url = "https://www.bbc.com/news"
    # url = "https://www.bbc.com/ukrainian"
    # bbc_page = get_html_source(url)
    bbc_page = get_html_source_from_folder()
    news_dict = parse_page(url, bbc_page)
    return news_dict
    # pprint.pp(news_dict)


if __name__ == '__main__':
    get_news()
