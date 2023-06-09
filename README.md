# Парсер книг с сайта  [tululu.org](https://tululu.org/)

Скачиваем книги с сайта [tululu.org](https://tululu.org/).  
Сохраняет книгу и обложку книги (если она есть) на диск.  
Скачивание происходит в заданном диапазоне (по умолчанию с `1` до `10`)  
Справка по скрипту:
```shell
python3 tululu.py --help
```

### Как установить

Требования: `python >= 3.10`   
Для запуска:
- Устанавливаем зависимости
```shell
pip install -r requirements.txt
```
- Запускаем парсер (для скачивания книг по id)
```shell
python3 tululu.py
```

- Запускаем парсер (для скачивания книг по жанрам)
```shell
python3 parse_tululu_category.py
```

### Аргументы
**Возможные аргументы скрипта `tululu.py`:**

- Опциональные:
  - `--start_id` - id начальной книги.
  - `--end_id` - id финальной книги.

Примеры использования:  
```shell
python3 tululu.py --end_id 10
```
```shell
python3 tululu.py --start_id 2 --end_id 15
```

**`start_id` не может быть больше `end_id`**

**Возможные аргументы скрипта `parse_tululu_category.py`:**

- Опциональные:
  - `--category_id` - id жанра(категории) откуда будем скачивать книги. Значение по умолчанию `55`
  - `--start_page` - номер страницы откуда начинаем скачивать. Значение по умолчанию `1`
  - `--end_page` - номер страницы до которой скачиваем (включительно). Значение по умолчанию `1`
  - `--dest_folder` - путь в какую папку будем сохранять результат начиная от папки `./docs`. Значение по умолчанию `./docs/static/`
  - `--skip_imgs` - Пропустить скачивание постеров. Значение по умолчанию `False`
  - `--skip_txt` - Пропустить скачивание книги. Значение по умолчанию `False`
  - `--json_path` - папка куда сохранить результирующий .json Значение по умолчанию текущая папка скрипта


Примеры использования:  
```shell
python3 parse_tululu_category.py --category_id 127
```
```shell
python3 parse_tululu_category.py --category_id 127 --json_path "./json" --start_page 1 --skip_imgs True
```

### Рендер сайта для визуального отображения скаченных книг

- Запускаем парсер для скачивания книг по категориям.  
Например: 
```shell
python3 parse_tululu_category.py --start_page 1 --end_page 10
```
- Рендерим страницы
```shell
python3 render_website.py
```
Если нам нужен локальный сервер с отслеживаем изменений в главном шаблоне с последующей перегенерацией страниц используем аргумент `--with_local_server`.  
Пример:
```shell
python3 render_website.py --with_local_server
```
- Создаем страницу в репозитории используя GitHub Pages.  
Как это сделать можно прочитать в официальной документации [здесь](https://docs.github.com/ru/pages)
- Смотрим сайт  
Пример сайта доступен по [ссылке](https://stranix.github.io/parser_library/pages/index1.html).

Сгенерированный сайт можно открывать локально, так же выкладывать на любой другой хостинг.  
Данные для сайта лежат в папке `./docs`

### Про логирование
Для настройки логирования используется файл logging_config.json  
Если файла с настройки нет, будет писаться стандартный ввывод библиотеки logging.  
Как заполнять logging_config.json можно прочитать [тут](https://docs-python.ru/standart-library/paket-logging-python/funktsija-dictconfig-modulja-logging-config/)

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
