import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from tqdm import *

headers = {
    'user-agent': generate_user_agent()
}

def get_html(url):
    r = requests.get(url, headers=headers, timeout=15)
    return r.text


def get_pars(html):
    soup = BeautifulSoup(html, 'lxml')
    head = soup.find('div', class_='stories-feed__container').find_all('article', class_="story")
    posts = []
    for ind in head:
        try:
            title = ind.find('a', class_='story__title-link').string
            img_link = {idx: url['data-large-image'] for idx, url in
                        enumerate(ind.find_all('img', class_="story-image__image"))}
            if title and img_link:
                posts.append([title, img_link.get(0)])
        except:
            pass
    return posts

def get_posts_pikabu():
    data = []
    main_url = 'https://pikabu.ru/tag/%D0%9C%D0%B5%D0%BC%D1%8B?q=%D1%8E%D0%BC%D0%BE%D1%80&r=3&page'
    for page in range(2):
        url = main_url + '=%s' % page
        data += get_pars(get_html(url))
    return data
