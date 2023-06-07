import re
import logging

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def parse_book_page(html_content: str) -> dict:
    """Парсим информацию по книге с сайта tululu.org.

    :param html_content: html страницы книги.

    :return: dict - данные по книге.
    """
    logger.info('Парсим информацию о книге')
    soup = BeautifulSoup(html_content, 'lxml')

    title_tag = soup.select_one('#content h1')
    split_title_tag = title_tag.text.split('::')

    book_title = split_title_tag[0].strip()
    book_author = split_title_tag[1].strip()

    book_poster_link = soup.select_one('.bookimage img')['src']

    comment_span_tags = soup.select('.texts span')
    comments = [comment.text for comment in comment_span_tags]

    genre_tags = soup.select('span.d_book :link')
    genres = [genre.text for genre in genre_tags]

    book = {
        'title': book_title,
        'author': book_author,
        'comments': comments,
        'genres': genres,
        'poster_link': book_poster_link
    }

    logger.debug('Полученная информация о книге: %s', book)
    logger.info('Завершено')

    return book


def parse_category_page(html_content: str) -> list[int]:
    """Парсим страницу с книгами по категории сайта tululu.org.

    :param html_content: html страницы с категорией.

    :return: list - список id книг из категории.
    """
    logger.info('Парсим информацию о книгах со страницы категории')
    book_ids = []

    soup = BeautifulSoup(html_content, 'lxml')
    tables_with_book_description = soup.select('table.d_book')
    for table in tables_with_book_description:
        table_row_with_book_link = table.select_one(':link')
        book_link = table_row_with_book_link.get('href')

        book_id = re.sub(r'\D', '', book_link)
        book_ids.append(int(book_id))

    logger.debug('Cписок id найденный книг %s', book_ids)
    logger.info('Завершено')

    return book_ids


def get_number_of_pages_in_category(html_content: str) -> int:
    """Получаем информацию о количестве страниц категории книг сайта tululu.org.

    :param html_content: html страницы с категорией.

    :return: int - количество страниц категории книг.
    """

    logger.info('Получаем информацию о количестве страниц категории книг')
    count_pages = 1
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        count_pages = soup.select_one('.npage:last-of-type').text
        logger.debug('Количество страниц: %s', count_pages)
        return int(count_pages)
    except AttributeError:
        logger.warning('Внимание. У категории только 1 страница книг')
        return count_pages
