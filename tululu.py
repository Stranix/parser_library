import sys
import json
import requests
import argparse
import logging
import logging.config

from services import fetch_book

logger = logging.getLogger(__name__)


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
        with open('logging_config.json', 'r', encoding='utf-8') as file:
            logging.config.dictConfig(json.load(file))
    except FileNotFoundError:
        logger.warning('Для настройки логирования нужен logging_config.json')

    logger.info('Старт парсера')

    parser = create_arg_parser()
    args = parser.parse_args()
    logger.debug('argparse %s', args)

    start_book_id = args.start_id
    end_book_id = args.end_id

    if start_book_id > end_book_id:
        logger.critical(
            'id стартовой книги не может быть больше id конечной книги'
        )
        raise KeyboardInterrupt

    for book_id in range(start_book_id, end_book_id):
        try:
            fetch_book(book_id)

        except requests.HTTPError:
            logger.error(
                'Не удалось скачать книгу или обложку. id - %s',
                book_id
            )


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        logger.info('Работа скрипта остановлена')

    finally:
        sys.exit()
