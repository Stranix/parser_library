import logging
import argparse
import sys

import more_itertools

from livereload import Server

from services import (
    get_jinja_template,
    get_books_from_json_file,
    save_rendered_page,
    configure_logging
)

logger = logging.getLogger(__name__)


def create_arg_parser():
    description = 'Генерируем сайт для скаченных книг с сайта tululu.org'
    epilog = """
    Генерация изначально расчитана на Github Pages.
    Шаблоны страниц сохраняются в папку docs/pages.
    """
    arg_parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog
    )

    arg_parser.add_argument('--only_render', '-r', action='store_true',
                            help='''Пропустить скачивание книги. 
                                    Значение по умолчанию False '''
                            )

    return arg_parser


def on_reload():
    """Генерируем страницы сайта с книгами.
    Генерация происходит при запуске скрипта или при включенном liveserver при
    изменении шаблона jinja
    """
    template = get_jinja_template('templates/template.html')

    books_chunked = list(
        more_itertools.chunked(
            get_books_from_json_file('downloaded_books_info.json'),
            20
        )
    )

    books_count = len(books_chunked)

    for page, books in enumerate(books_chunked, start=1):
        rendered_page = template.render(
            books=books,
            books_count=books_count,
            current_page=page
        )
        save_rendered_page(f'index{page}.html', rendered_page)


if __name__ == '__main__':
    try:
        configure_logging()

        logger.info('Страт генерации страниц сайта')

        parser = create_arg_parser()
        args = parser.parse_args()
        logger.debug('argparse %s', args)

        only_render = args.only_render

        on_reload()

        if only_render:
            logger.info('Рендер выполнен. Завершаю работу')
            raise KeyboardInterrupt

        server = Server()
        server.watch('templates/template.html', on_reload)
        server.serve(root='docs/pages/', default_filename='index1.html')

    except FileNotFoundError:
        logger.critical(
            'Для работы необходим файл с книгами %s в корне проекта',
            'downloaded_books_info.json'
        )
        sys.exit()

    except KeyboardInterrupt:
        logger.warning('Завершение работы')

