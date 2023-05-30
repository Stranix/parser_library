from urllib.parse import urljoin

import requests

from parser import parse_category_page
from services import check_for_redirect


def parse_category(category_id: int):
    # скачиваем страницу https://tululu.org/l55/
    response = requests.get('https://tululu.org/l55/')
    response.raise_for_status()
    check_for_redirect(response)
    # находим первую книгу с научной фантастикой
    book_link = urljoin(response.url, parse_category_page(response.text))
    # выводим ссылку на книгу для послед скачивания
    print(book_link)
