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
- Запускаем парсер
```shell
python3 tululu.py
```

### Аргументы
Возможные аргументы скрипта:
- Позиционные:
  - `start` - id начальной книги.
  - `end` - id финальной книги.
  

- Опциональные:
  - `--start_id` - id начальной книги.
  - `--end_id` - id финальной книги.

Примеры использования:  
```shell
python3 tululu.py 20 30
```
```shell
python3 tululu.py 1 --end_id 10
```
```shell
python3 tululu.py --start_id 2 --end_id 15
```

**`start_id` не может быть больше `end_id`**

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
