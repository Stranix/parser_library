import sys
import argparse

from services import fetch_book
from services import get_category_end_page
from services import save_books_info_as_json_file
from services import get_books_id_in_range_pages_in_category


def create_arg_parser():
    description = 'Качаем книги в выбранной категории с сайта tululu.org'
    epilog = """
    Скаченные книги сохраняются в папку ./books
    Скаченные обложки книг сохраняются в папку ./images
    """
    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog
    )

    arg_parser.add_argument('--category_id', default=55, metavar='', type=int,
                            help='''id книги с которой начнем парсить. 
                                Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--start_page', default=1, metavar='', type=int,
                            help='''id книги с которой начнем парсить. 
                            Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--end_page', default=1, metavar='', type=int,
                            help='''id книги до которой парсим. 
                            Значение по умолчанию 11 '''
                            )

    return arg_parser


def main():
    try:
        parser = create_arg_parser()
        args = parser.parse_args()
        category_id = args.category_id
        category_start_page = args.start_page
        category_end_page = args.end_page

        category_end_page_on_site = get_category_end_page(category_id)
        if category_end_page > category_end_page_on_site:
            print('Страниц у выбранной категории:', category_end_page_on_site)
            print('Поменяйте диапазон для скачивания')
            raise KeyboardInterrupt

        if category_start_page > category_end_page:
            category_end_page = category_end_page_on_site

        books_id = get_books_id_in_range_pages_in_category(
            category_id,
            category_start_page,
            category_end_page + 1
        )

        if not books_id:
            print('Не нашел книг для скачивания. Проверьте диапазон страниц')
            raise KeyboardInterrupt

        downloaded_books_info = []
        for book_id in books_id:
            book = fetch_book(book_id)

            if not book:
                continue

            book.download_link = f'{book.download_link}?id={book.id}'
            downloaded_books_info.append(book.__dict__)

        if downloaded_books_info:
            save_books_info_as_json_file(
                'downloaded_books_info.json',
                downloaded_books_info
            )

    except KeyboardInterrupt:
        print('Работа скрипта остановлена')
        sys.exit()


if __name__ == '__main__':
    main()
