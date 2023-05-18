import sys
import argparse

from services import fetch_books
from parser import parse_script_args


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

    arg_parser.add_argument('--start_id', default=1, metavar='', type=int,
                            help='''id книги с которой начнем парсить. 
                            Значение по умолчанию 1 '''
                            )

    arg_parser.add_argument('--end_id', default=11, metavar='', type=int,
                            help='''id книги до которой парсим. 
                            Значение по умолчанию 11 '''
                            )

    return arg_parser


def main():
    try:
        parser = create_arg_parser()
        start_book_id, end_book_id = parse_script_args(parser)
        for book_id in range(start_book_id, end_book_id):
            fetch_books(book_id)
    except KeyboardInterrupt:
        print('Работа скрипта остановлена')
        sys.exit()


if __name__ == '__main__':
    main()
