import os
import urllib
import requests

from urllib.parse import urljoin
from dataclasses import dataclass
from pathvalidate import sanitize_filename

from parser import parse_book_page


@dataclass
class Book:
    id: int
    title: str
    author: str
    comments: list
    genres: list
    download_link: str = ''
    poster_link: str = ''


def check_for_redirect(response: requests.Response):
    """Проверяет редирект на главную страницу.

    В случаи редиректа бросает исключение.

    :param response: Ответ сайта tululu.org.
    """

    response.raise_for_status()
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def fetch_books(start_id: int, end_id: int):
    """Качает и сохраняет в диапазоне книги и обложки с сайта tululu.org.

    :param start_id: Id первой книги.
    :param end_id: Id последней книги.

    :return: tuple(id стартовой книги, id конечной книги).
    """

    for book_id in range(start_id, end_id):
        try:
            book = get_book(book_id)
            file_name = '{}_{}'.format(book_id, book.title)
            download_txt(book.download_link, file_name)
            download_image(book.poster_link)
        except requests.HTTPError:
            print('Не удалось скачать книгу или обложку. id -', book_id)
            continue


def download_txt(url, filename, folder='books/') -> str:
    """Качает текстовый файл по-указанному url и сохраняет на диск.

    :param url: ссылка на скачивание.
    :param filename: имя для сохранения.
    :param folder:папка для сохранения (будет создана если её нет)

    :return: str - Строку с указанием куда сохранили файл.
    """

    response = requests.get(url)
    check_for_redirect(response)

    filename = sanitize_filename('{}.txt'.format(filename))
    return save_file(folder, filename, response.content)


def download_image(url, folder='images/') -> str:
    """Качает картинку по-указанному url и сохраняет на диск.

    :param url: ссылка на скачивание.
    :param folder:папка для сохранения (будет создана если её нет)

    :return: str - Строку с указанием куда сохранили файл.
    """

    response = requests.get(url)
    check_for_redirect(response)

    filename = get_image_name_from_url(url)
    return save_file(folder, filename, response.content)


def get_book(book_id: int) -> Book:
    """Получаем книгу (Book) по-указанному id.

    :param book_id: id книги для скачивания.

    :return: Book - информация по книге
    """

    url = '{}b{}/'.format('https://tululu.org/', book_id)
    response = requests.get(url)
    check_for_redirect(response)

    book = parse_book_page(response.text)
    book['id'] = book_id
    book['download_link'] = urljoin(
        'https://tululu.org/',
        f'txt.php?id={book_id}'
    )

    return Book(**book)


def get_image_name_from_url(url: str) -> str:
    """Получаем имя картинки из url.

    :param url: ссылка на картинку.

    :return: str - имя картинки
    """

    split_result = urllib.parse.urlsplit(url)
    url_path = split_result.path
    return url_path.split('/')[-1]


def save_file(folder: str, filename: str, content: bytes) -> str:
    """Сохраняет файл на диск.

    :param folder: папка для сохранения.
    :param filename: имя файла.
    :param content: байтовое преставление для сохранения.

    :return: str - путь куда сохранил
    """

    path_to_save = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_save, mode='wb') as file:
        file.write(content)
    return path_to_save
