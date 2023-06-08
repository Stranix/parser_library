import os
import json
import more_itertools

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def save_rendered_page(filename: str, rendered_page: str) -> str:
    with open(filename, 'w', encoding="utf8") as file:
        file.write(rendered_page)
    return filename


def get_books_from_json_file(filename: str) -> dict:
    with open(filename, 'r') as json_file:
        books = json.load(json_file)
    return books


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    os.makedirs('pages', exist_ok=True)

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
        path_to_save = os.path.join('pages/', f'index{page}.html')
        save_rendered_page(path_to_save, rendered_page)


if __name__ == '__main__':
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
