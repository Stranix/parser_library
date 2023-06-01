import sys
import requests
import argparse

from services import fetch_book


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
    parser = create_arg_parser()
    args = parser.parse_args()
    start_book_id = args.start_id
    end_book_id = args.end_id

    if start_book_id > end_book_id:
        print('id стартовой книги не может быть больше id конечной книги')
        sys.exit()

    for book_id in range(start_book_id, end_book_id):
        try:
            fetch_book(book_id)

        except requests.HTTPError:
            print('Не удалось скачать книгу или обложку. id -', book_id)


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('Работа скрипта остановлена')

    finally:
        sys.exit()
