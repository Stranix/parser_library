import os
import requests


def main():
    print(f'Hi')
    folder_for_save = './books'
    os.makedirs(folder_for_save, exist_ok=True)

    for number in range(1, 11):
        print(number)
        url = f'https://tululu.org/txt.php?id={number}'
        response = requests.get(url)
        file_name = './book_{}.txt'.format(number)

        if response.status_code == 200:
            with open(folder_for_save + file_name, mode='wb') as file:
                file.write(response.content)


if __name__ == '__main__':
    main()

