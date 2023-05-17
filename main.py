import os
import sys
import urllib
import argparse
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import dataclass
from pathvalidate import sanitize_filename


SITE_LINK = 'https://tululu.org/'


def create_arg_parser():
    description = 'Качаем книги для деда =)'
    epilog = """
    Скаченные книги сохраняются в папку ./books
    Скаченные обложки книг сохраняются в папку ./images
    """
    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog
    )
    arg_parser.add_argument('start', default=1, metavar='', type=int,
                            help='''id книги с которой начнем парсить. 
                                Значение по умолчанию 1 ''', nargs='?'
                            )
    arg_parser.add_argument('end', default=11, metavar='', type=int,
                            help='''id книги до которой парсим. 
                                Значение по умолчанию 11 ''', nargs='?'
                            )
    arg_parser.add_argument('--start_id', metavar='', type=int,
                            help='''id книги с которой начнем парсить. 
                            Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--end_id', metavar='', type=int,
                            help='''id книги до которой парсим. 
                            Значение по умолчанию 11 '''
                            )

    return arg_parser


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
    response.raise_for_status()
    if response.url == SITE_LINK:
        raise requests.HTTPError


def fetch_books(start_id: int, end_id: int):
    for book_id in range(start_id, end_id):
        try:
            book = get_book(book_id)
            file_name = '{}_{}'.format(book_id, book.title)
            download_txt(book.download_link, file_name)
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
    check_for_redirect(response)

    book = parse_book_page(response.text)
    book['id'] = book_id
    book['download_link'] = urljoin(SITE_LINK, f'txt.php?id={book_id}')

    return Book(**book)


def get_image_name_from_url(url: str) -> str:
    split_result = urllib.parse.urlsplit(url)
    url_path = split_result.path
    return url_path.split('/')[-1]


def parse_book_page(html_content: str) -> dict:
    soup = BeautifulSoup(html_content, 'lxml')
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

    book = {
        'title': book_title,
        'author': book_author,
        'comments': comments,
        'genres': genres,
        'poster_link': book_poster_link
    }

    return book


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    start_id = args.start
    end_id = args.end

    if args.start_id:
        start_id = args.start_id

    if args.end_id:
        end_id = args.end_id

    if start_id > end_id:
        print('id стартовой книги не может быть больше id конечной книги')
        sys.exit()

    fetch_books(start_id, end_id)


if __name__ == '__main__':
    main()
