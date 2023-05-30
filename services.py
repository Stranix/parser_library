import os
import json
import time
import urllib
import requests

from urllib.parse import urljoin
from dataclasses import dataclass
from pathvalidate import sanitize_filename

from parser import parse_book_page
from parser import parse_category_page


@dataclass
class Book:
    id: int
    title: str
    author: str
    comments: list
    genres: list
    download_link: str = ''
    poster_link: str = ''
    book_saved_path: str = ''
    poster_saved_path: str = ''


def check_for_redirect(response: requests.Response):
    """Проверяет редирект на главную страницу.

    В случаи редиректа бросает исключение.

    :param response: Ответ сайта tululu.org.
    """

    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def fetch_book(book_id: int) -> Book:
    """Качает и сохраняет книгу и обложку с сайта tululu.org.

    :param book_id: ID книги для скачивания.

    :return: tuple(id стартовой книги, id конечной книги).
    """

    while True:
        try:
            book = get_book(book_id)

            request_params = {
                'id': book.id
            }
            file_name = '{}_{}'.format(book_id, book.title)

            book_saved_path = download_txt(
                book.download_link,
                file_name,
                request_params
            )

            poster_saved_path = download_image(book.poster_link)

            book.book_saved_path = book_saved_path
            book.poster_saved_path = poster_saved_path

            return book

        except requests.HTTPError:
            print('Не удалось скачать книгу или обложку. id -', book_id)
            break

        except (requests.ConnectionError, requests.ConnectTimeout):
            print(
                'Ошибка соединения, попытаюсь через 5 секунд повторно '
                'скачать книгу'
            )
            time.sleep(5)


def download_txt(url, filename, params=None, folder='books/') -> str:
    """Качает текстовый файл по-указанному url и сохраняет на диск.

    :param url: ссылка на скачивание.
    :param filename: имя для сохранения.
    :param folder: папка для сохранения (будет создана если её нет)
    :param params: дополнительные параметры запроса

    :return: str - Строку с указанием куда сохранили файл.
    """

    response = requests.get(url, params)
    response.raise_for_status()
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
    response.raise_for_status()
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
    response.raise_for_status()
    check_for_redirect(response)

    book = parse_book_page(response.text)

    book['id'] = book_id
    book['poster_link'] = urljoin(response.url, book['poster_link'])
    book['download_link'] = urljoin(response.url, '/txt.php')
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


def save_books_info_as_json_file(filename: str, books_info: list):
    """Сохраняет информацию в json файл о скаченных книгах в категории.

    :param filename: имя файла.
    :param books_info: список словарей с информацией о скаченных книгах.
    """

    with open(filename, mode='w') as file:
        json.dump(books_info, file, indent=4, ensure_ascii=False)


def get_books_id_in_range_pages_in_category(
        category_id: int,
        start_page: int = 1,
        end_page: int = 1
) -> list[int]:
    """Получаем id книг выбранной категории и страниц с сайта tululu.org.

    :param category_id: id книжной категории.
    :param start_page: номер страницы категории откуда начинаем парсить.
    :param end_page: номер страницы категории на которой заканчиваем парсить.

    :return: list - список id найденных книг в выбранном диапазоне
    """

    books_id = []

    for category_page in range(start_page, end_page + 1):
        books_id_on_page = get_books_id_from_category_page(
            category_id,
            category_page
        )
        books_id.extend(books_id_on_page)

    return books_id


def get_books_id_from_category_page(
        category_id: int,
        category_page: int
) -> list[int] | None:
    """Получаем информацию о id книгах на конкретной страницы категории.

    :param category_id: id книжной категории.
    :param category_page: страница категории.

    :return: list - список найденных id книг на странице категории.
    """

    url = f'https://tululu.org/l{category_id}/{category_page}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    books_id = parse_category_page(response.text)

    if books_id:
        return books_id
