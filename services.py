import os
import json
import time
import urllib
import logging
import requests

from urllib.parse import urljoin
from dataclasses import dataclass
from pathvalidate import sanitize_filename

from parser import parse_book_page
from parser import parse_category_page
from parser import get_number_of_pages_in_category


logger = logging.getLogger(__name__)


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
    logger.info('Проверка редиректа на главную страницу')
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def fetch_book(
        book_id: int,
        dest_folder: str = './',
        skip_imgs: bool = False,
        skip_txt: bool = False
) -> Book:
    """Качает и сохраняет книгу и обложку с сайта tululu.org.

    :param book_id: ID книги для скачивания.
    :param dest_folder: корневая папка для сохранения результата.
    :param skip_imgs: скачивать или не скачивать постеры к книге.
    :param skip_txt: скачивать или не скачивать книгу.

    :return: tuple(id стартовой книги, id конечной книги).
    """
    logger.info('фетчим книгу с id - %s', book_id)
    while True:
        try:
            book = get_book(book_id)

            request_params = {
                'id': book.id
            }
            file_name = '{}_{}'.format(book_id, book.title)

            logger.debug('file_name: %s', file_name)

            logger.debug('skip_txt: %s', skip_txt)
            if not skip_txt:
                book_saved_path = download_txt(
                    book.download_link,
                    file_name,
                    request_params,
                    dest_folder
                )
                book.book_saved_path = book_saved_path

            logger.debug('skip_imgs: %s', skip_imgs)
            if not skip_imgs:
                poster_saved_path = download_image(
                    book.poster_link,
                    dest_folder
                )
                book.poster_saved_path = poster_saved_path

            logger.debug('book: %s', book)
            logger.info('Завершено')
            return book

        except (requests.ConnectionError, requests.ConnectTimeout):
            logger.error(
                'Ошибка соединения, попытаюсь через 5 секунд повторно '
                'скачать книгу'
            )
            time.sleep(5)


def download_txt(
        url,
        filename,
        params=None,
        dest_folder='./',
        subfolder='books/'
) -> str:
    """Качает текстовый файл по-указанному url и сохраняет на диск.

    :param url: ссылка на скачивание.
    :param filename: имя для сохранения.
    :param dest_folder: основная папка для сохранения книги.
    :param subfolder: подпапка для сохранения книги (будет создана если её нет)
    :param params: дополнительные параметры запроса

    :return: str - Строку с указанием куда сохранили файл.
    """
    logger.info('Скачиваем текстовую версию книги')
    logger.debug('url: %s', url)

    response = requests.get(url, params)
    logger.debug('response status code: %s', response.status_code)
    response.raise_for_status()
    check_for_redirect(response)

    folder = os.path.join(dest_folder, subfolder)
    logger.debug('Папка для сохранения: %s', folder)

    filename = sanitize_filename('{}.txt'.format(filename))
    logger.debug('Имя файла: %s', filename)
    logger.info('информация получена. Попытка сохранить файл')
    return save_file(folder, filename, response.content)


def download_image(url, dest_folder='./', subfolder='images/') -> str:
    """Качает картинку по-указанному url и сохраняет на диск.

    :param url: ссылка на скачивание.
    :param dest_folder: основная папка для сохранения постера.
    :param subfolder: подпапка для сохранения постеров (будет создана если её нет)

    :return: str - Строку с указанием куда сохранили файл.
    """
    logger.info('Скачиваем обложку книги')
    logger.debug('url: %s', url)

    response = requests.get(url)
    logger.debug('response status code: %s', response.status_code)
    response.raise_for_status()
    check_for_redirect(response)

    folder = os.path.join(dest_folder, subfolder)
    logger.debug('Папка для сохранения: %s', folder)

    filename = get_image_name_from_url(url)
    logger.debug('Имя файла: %s', filename)
    logger.info('информация получена. Попытка сохранить файл')

    return save_file(folder, filename, response.content)


def get_book(book_id: int) -> Book:
    """Получаем книгу (Book) по-указанному id.

    :param book_id: id книги для скачивания.

    :return: Book - информация по книге
    """
    logger.info('Загружаем информацию с сайта о книге')

    url = '{}b{}/'.format('https://tululu.org/', book_id)
    logger.debug('url: %s', url)

    response = requests.get(url)
    logger.debug('response status code: %s', response.status_code)
    response.raise_for_status()
    check_for_redirect(response)

    book = parse_book_page(response.text)

    book['id'] = book_id
    book['poster_link'] = urljoin(response.url, book['poster_link'])
    book['download_link'] = urljoin(response.url, '/txt.php')

    logger.info('Завершено')
    return Book(**book)


def get_image_name_from_url(url: str) -> str:
    """Получаем имя картинки из url.

    :param url: ссылка на картинку.

    :return: str - имя картинки
    """
    logger.info('Получаем имя изображения из url: %s', url)
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
    logger.info(
        'Сохраняем файл на диск в паку %s с именем %s',
        folder,
        filename
    )
    path_to_save = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    with open(path_to_save, mode='wb') as file:
        file.write(content)
    logger.info('Сохранено')
    return path_to_save


def save_books_as_json_file(
        filename: str,
        books: list,
        json_path: str = './'
) -> str:
    """Сохраняет информацию в json файл о скаченных книгах в категории.

    :param filename: имя файла.
    :param books: список словарей с информацией о скаченных книгах.
    :param json_path: путь до каталога куда сохраняем файл с результатом.

    :return: str - путь куда сохранил
    """
    logger.info('Сохраняем информацию о книге в файл %s', filename)
    path_to_save = os.path.join(json_path, filename)
    os.makedirs(json_path, exist_ok=True)
    with open(path_to_save, mode='w') as file:
        json.dump(books, file, indent=4, ensure_ascii=False)

    logger.info('Сохранено')
    return path_to_save


def get_book_ids_in_range_pages_in_category(
        category_id: int,
        start_page: int = 1,
        end_page: int = 2
) -> list[int]:
    """Получаем id книг выбранной категории и страниц с сайта tululu.org.

    :param category_id: id книжной категории.
    :param start_page: номер страницы категории откуда начинаем парсить.
    :param end_page: номер страницы категории на которой заканчиваем парсить.

    :return: list - список id найденных книг в выбранном диапазоне
    """

    logger.info('Получаем айденты книг в категории %s', category_id)

    book_ids = []

    for category_page in range(start_page, end_page):
        while True:
            try:
                book_ids_on_page = get_book_ids_from_category_page(
                    category_id,
                    category_page
                )
                book_ids.extend(book_ids_on_page)
                break
            except requests.HTTPError:
                error_msg = 'Ошибка при парсинге страницы {} категории {}'.format(
                    category_page,
                    category_id
                )
                logger.error(error_msg)
                break
            except (requests.ConnectionError, requests.ConnectTimeout):
                logger.error(
                    'Ошибка соединения, попытаюсь через 5 секунд повторно '
                    'получить данные со страницы '
                )
                time.sleep(5)
    logger.debug('book_ids: %s', book_ids)
    logger.info('Айденты книг получены')

    return book_ids


def get_book_ids_from_category_page(
        category_id: int,
        category_page: int
) -> list:
    """Получаем информацию о id книгах на конкретной страницы категории.

    :param category_id: id книжной категории.
    :param category_page: страница категории.

    :return: list - список найденных id книг на странице категории.
    """
    logger.info(
        'Получаем информацию о id книгах на конкретной страницы категории.'
    )

    url = f'https://tululu.org/l{category_id}/{category_page}/'
    logger.debug('url: %s', url)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    book_ids = parse_category_page(response.text)

    logger.debug('book_ids: %s', book_ids)
    logger.info('Получил айденты книг с конкретной страницы категории')

    return book_ids


def get_category_end_page(category_id: int) -> int:
    """Получаем информацию о количестве страниц в выбранной категории.

    :param category_id: id книжной категории.

    :return: int - сколько всего страниц в выбранной категории.
    """
    logger.info(
        'Получаем информацию о количестве страниц в выбранной категории %s',
        category_id
    )

    url = f'https://tululu.org/l{category_id}/'
    logger.debug('url: %s', url)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    return get_number_of_pages_in_category(response.text)
