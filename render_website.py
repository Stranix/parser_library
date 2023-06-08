import json

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape


def save_rendered_page(filename: str, rendered_page: str) -> str:
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    return filename


def get_books_from_json_file(filename: str) -> dict:
    with open(filename, 'r') as json_file:
        books = json.load(json_file)
    return books


def on_reload() -> str:
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        books=get_books_from_json_file('downloaded_books_info.json'),
    )

    return save_rendered_page('index.html', rendered_page)


if __name__ == '__main__':
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')
