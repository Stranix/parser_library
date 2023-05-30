from urllib.parse import urljoin

import requests

from parser import parse_category_page
from services import check_for_redirect


def parse_category(category_id: int):
    # скачиваем страницу https://tululu.org/l55/
    response = requests.get('https://tululu.org/l55/')
    response.raise_for_status()
    check_for_redirect(response)
    # находим все книги с научной фантастикой на странице
    for book_link in parse_category_page(response.text):
        book_link_abs = urljoin(response.url, book_link)
        # выводим ссылку на книгу для последующего скачивания
        print(book_link_abs)
