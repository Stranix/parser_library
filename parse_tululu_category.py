import time
from urllib.parse import urljoin

import requests

from parser import parse_category_page
from services import check_for_redirect


def parse_category(category_id: int):
    # скачиваем страницу https://tululu.org/l55/
    for category_page in range(1, 11):
        url = f'https://tululu.org/l55/{category_page}/'
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
        # находим все книги с научной фантастикой на странице
        for book_link in parse_category_page(response.text):
            book_link_abs = urljoin(response.url, book_link)
            # выводим ссылку на книгу для последующего скачивания
            print(book_link_abs)

        time.sleep(1)
