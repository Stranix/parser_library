import sys
import argparse

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_script_args(parser: argparse.ArgumentParser) -> tuple:
    """Парсит аргументы скрипта.

    :param parser: Аргументы скрипта.
    :return: tuple(id стартовой книги, id конечной книги).
    """
    args = parser.parse_args()
    start_id = args.start_id
    end_id = args.end_id

    if start_id > end_id:
        print('id стартовой книги не может быть больше id конечной книги')
        sys.exit()

    return start_id, end_id


def parse_book_page(html_content: str) -> dict:
    """Парсим информацию по книге с сайта tululu.org.

    :param html_content: html страницы книги.

    :return: dict - данные по книге.
    """

    soup = BeautifulSoup(html_content, 'lxml')
    title_tag = soup.find('h1')
    split_title_tag = title_tag.text.split('::')

    book_title = split_title_tag[0].strip()
    book_author = split_title_tag[1].strip()

    book_poster_link = soup.find('div', class_='bookimage') \
        .find('img') \
        .get('src')

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
