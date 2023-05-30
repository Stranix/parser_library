import sys

from services import fetch_book
from services import save_books_info_as_json_file
from services import get_books_id_in_range_pages_in_category


def main():
    try:
        books_id = get_books_id_in_range_pages_in_category(
            category_id=55,
            end_page=2
        )

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
