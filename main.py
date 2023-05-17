import os
import requests


def check_for_redirect(response: requests.Response):
    response.raise_for_status()
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def main():
    print(f'Hi')
    folder_for_save = './books'
    os.makedirs(folder_for_save, exist_ok=True)

    for number in range(1, 11):
        print(number)
        url = f'https://tululu.org/txt.php?id={number}'
        try:
            response = requests.get(url)
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        file_name = './book_{}.txt'.format(number)
        with open(folder_for_save + file_name, mode='wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()
