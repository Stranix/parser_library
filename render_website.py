import json

from jinja2 import Environment, FileSystemLoader, select_autoescape


if __name__ == '__main__':
    with open('downloaded_books_info.json', 'r') as json_file:
        books = json.load(json_file)

    env = Environment(
        loader=FileSystemLoader('./html'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        books=books,
    )

    with open('html/index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
