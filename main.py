import os
import urllib
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from dataclasses import dataclass

SITE_LINK = 'https://tululu.org/'


@dataclass
class Book:
    id: int
    title: str
    author: str
    comments: list
    genres: list
    poster_link: str = ''


def check_for_redirect(response: requests.Response):
    response.raise_for_status()
    if response.url == SITE_LINK:
        raise requests.HTTPError


def fetch_books():
    for book_id in range(1, 11):
        try:
            book = get_book(book_id)
            url = '{}txt.php?id={}'.format(SITE_LINK, book.id)
            file_name = '{}_{}'.format(book_id, book.title)
            download_txt(url, file_name)
            download_image(book.poster_link)
        except requests.HTTPError:
            continue


def download_txt(url, filename, folder='books/') -> str:
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    check_for_redirect(response)
    filename = sanitize_filename('{}.txt'.format(filename))
    path_to_save = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_save, mode='wb') as file:
        file.write(response.content)
    return path_to_save


def download_image(url, folder='images/') -> str:
    """Функция для скачивания картинок.
    Args:
        url (str): Cсылка на изображение, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    check_for_redirect(response)

    filename = get_image_name_from_url(url)
    path_to_save = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_save, mode='wb') as file:
        file.write(response.content)
    return path_to_save


def get_book(book_id: int) -> Book:
    url = '{}b{}/'.format(SITE_LINK, book_id)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    split_title_tag = title_tag.text.split('::')

    book_title = split_title_tag[0].strip()
    book_author = split_title_tag[1].strip()

    book_poster_link = soup.find('div', class_='bookimage') \
        .find('img') \
        .get('src')
    book_poster_link = urljoin(SITE_LINK, book_poster_link)

    comment_div_tags = soup.find_all('div', class_='texts')
    comments = [comment.find('span').text for comment in comment_div_tags]

    genre_tags = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genre_tags]

    return Book(
        book_id,
        book_title,
        book_author,
        comments,
        genres,
        book_poster_link
    )


def get_image_name_from_url(url: str) -> str:
    split_result = urllib.parse.urlsplit(url)
    url_path = split_result.path
    return url_path.split('/')[-1]


def main():
    fetch_books()


if __name__ == '__main__':
    main()
