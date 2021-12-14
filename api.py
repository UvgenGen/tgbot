from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://bookshake.net/'


def search_books(query: list) -> list:
    params = {'q': '+'.join(query)}
    r = requests.get(urljoin(BASE_URL, 'search'), params=params)
    soup = BeautifulSoup(r.text, 'html.parser')
    books = []
    for tag in soup.find_all('div', 'book-card__meta'):
        name, *authors = tag.find_all('a')
        books.append(
            {
                'name': name.string,
                'url': name['href'],
                'authors': [author.string for author in authors]
            }
        )
    return books


def get_book_deatils(url: str) -> object:
    datails_url = urljoin(BASE_URL, url)
    r = requests.get(datails_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {
        'name': soup.find('h1', 'first-heading').string,
    }

    r = requests.get(urljoin(datails_url, '#download'))
    soup = BeautifulSoup(r.text, 'html.parser')
    download_urls = []
    for link in soup.find_all('a', 'btn-download'):
        download_urls.append(
            {
                'text': link.string.strip(),
                'url': urljoin(BASE_URL, link['href']),
            }
        )

    data.update({'download_urls': download_urls})

    return data