import json
import os
from http import HTTPStatus

import requests

from exceptions import FileNotGet, FileNotSave
from settings import Settings
from utils.log import print_log

settings = Settings()


async def get_file(data: dict[str, str]) -> dict[str, str] | None:
    """Получение информации о файле, отправленном юзером в бот."""
    method = f'{settings.API_URL}/getFile'
    file = requests.post(method, data=data)
    if file.status_code != HTTPStatus.OK:
        raise FileNotGet('Файл не скачан с сервера Телеграм')
    await print_log('info', 'Получена информация о файле с сервера Телеграм')
    return json.loads(file._content)['result']


async def save_file(file_data: dict[str, str], chat_id: int) -> str | None:
    """Сохраняем файл, отправленный юзером в бот."""
    if not os.path.exists(settings.DIR):
        os.makedirs(settings.DIR)
    path = file_data["file_path"]
    url = f'{settings.API_FILE_URL}/{path}'
    file_name = f'{chat_id}-{file_data["file_unique_id"]}.{path[-3:]}'
    with open(f'{settings.DIR}/{file_name}', "wb") as f:
        file = requests.get(url)
        if file.status_code != HTTPStatus.OK:
            raise FileNotGet('Файл не скачан с сервера Телеграм')
        await print_log('info', 'Получен файл с серверов Телеграма')
        try:
            f.write(file.content)
        except Exception as e:
            raise FileNotSave('Файл не сохранен на диск') from e
    await print_log('info', f'Файл сохранён на диск {file_name}')
    return file_name
