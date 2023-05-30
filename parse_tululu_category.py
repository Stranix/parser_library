import sys

from services import fetch_books_by_category
from services import save_books_info_as_json_file


def main():
    try:
        downloaded_books_info = fetch_books_by_category(
            category_id=55,
            pages=2
        )
        save_books_info_as_json_file(
            'downloaded_books_info.json',
            downloaded_books_info
        )
    except KeyboardInterrupt:
        print('Работа скрипта остановлена')
        sys.exit()


if __name__ == '__main__':
    main()
