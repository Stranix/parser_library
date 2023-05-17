import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from dataclasses import dataclass


@dataclass
class Book:
    id: int
    title: str
    author: str
    poster_link: str = ''


def check_for_redirect(response: requests.Response):
    response.raise_for_status()
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def fetch_books():
    for book_id in range(1, 11):
        try:
            book = get_book(book_id)
            url = f'https://tululu.org/txt.php?id={book.id}'
            file_name = '{}_{}'.format(book_id, book.title)
            download_txt(url, file_name)
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


def get_book(book_id: int) -> Book:
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('h1')
    split_title_tag = title_tag.text.split('::')

    book_title = split_title_tag[0].strip()
    book_author = split_title_tag[1].strip()

    return Book(book_id, book_title, book_author)


def main():
    fetch_books()


if __name__ == '__main__':
    main()
