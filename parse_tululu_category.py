import sys
import logging
import requests
import argparse

from dataclasses import asdict

from services import fetch_book
from services import configure_logging
from services import get_category_end_page
from services import save_books_as_json_file
from services import get_book_ids_in_range_pages_in_category


logger = logging.getLogger(__name__)


def create_arg_parser():
    description = 'Качаем книги в выбранной категории с сайта tululu.org'
    epilog = """
    Скаченные книги сохраняются в подпапку /books
    Скаченные обложки книг сохраняются в подпапку /images
    """
    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog
    )

    arg_parser.add_argument('--category_id', default=55, metavar='', type=int,
                            help='''id жанра(категории) откуда будем скачивать книги. 
                            Значение по умолчанию 55'''
                            )

    arg_parser.add_argument('--start_page', default=1, metavar='', type=int,
                            help='''номер страницы откуда начинаем скачивать. 
                            Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--end_page', default=1, metavar='', type=int,
                            help='''номер страницы до которой скачиваем (включительно). 
                            Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--dest_folder', default='media/', metavar='',
                            type=str,
                            help='''путь в какую папку будем сохранять результат. 
                                Значение по умолчанию ./media/ '''
                            )

    arg_parser.add_argument('--skip_imgs', action='store_true',
                            help='''Пропустить скачивание постеров. 
                                    Значение по умолчанию False '''
                            )

    arg_parser.add_argument('--skip_txt', action='store_true',
                            help='''Пропустить скачивание книги. 
                                    Значение по умолчанию False '''
                            )

    arg_parser.add_argument('--json_path', default='./', metavar='', type=str,
                            help='''папка куда сохранить результирующий .json 
                            Значение по умолчанию текущая папка скрипта '''
                            )

    return arg_parser


def main():
    configure_logging()

    logger.info('Старт парсера')

    parser = create_arg_parser()
    args = parser.parse_args()
    logger.debug('argparse %s', args)

    category_id = args.category_id
    category_start_page = args.start_page
    category_end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt
    json_path = args.json_path

    category_end_page_on_site = get_category_end_page(category_id)
    logger.debug(
        'Страниц %s у выбранной категории %s',
        category_end_page_on_site,
        category_id
    )

    if category_end_page > category_end_page_on_site:
        logger.critical(
            'Страниц у выбранной категории %s \n'
            'Поменяйте диапазон для скачивания',
            category_end_page_on_site,

        )
        raise KeyboardInterrupt

    if category_start_page > category_end_page:
        category_end_page = category_end_page_on_site

    book_ids = get_book_ids_in_range_pages_in_category(
        category_id,
        category_start_page,
        category_end_page + 1
    )

    if not book_ids:
        logger.critical(
            'Не нашел книг для скачивания. Проверьте диапазон страниц'
        )
        raise KeyboardInterrupt

    books = []
    for book_id in book_ids:
        try:
            book = fetch_book(book_id, dest_folder, skip_imgs, skip_txt)
            book.download_link = f'{book.download_link}?id={book.id}'
            books.append(asdict(book))
        except requests.HTTPError:
            logger.error(
                'Не удалось скачать книгу или обложку. id - %s',
                book_id
            )

    if books:
        save_books_as_json_file(
            'downloaded_books_info.json',
            books,
            json_path,
        )


if __name__ == '__main__':
    try:
        main()

    except requests.HTTPError:
        logger.critical(
            'Не смог определить количество доступных страниц категории'
        )

    except KeyboardInterrupt:
        logger.info('Работа скрипта остановлена')

    finally:
        sys.exit()
