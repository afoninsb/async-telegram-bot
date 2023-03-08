import json
import os
from http import HTTPStatus

import requests

import settings


async def get_file(data: dict[str, str]) -> dict[str, str] | None:
    """Получение информации о файле, отправленном юзером в бот."""
    method = f'{settings.API_URL}/getFile'
    file = requests.post(method, data=data)
    if file.status_code != HTTPStatus.OK:
        return
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
            return
        try:
            f.write(file.content)
        except Exception:
            return
    return file_name
