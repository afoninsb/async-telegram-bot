import asyncio
from http import HTTPStatus
from typing import Union
import aiohttp
from aiohttp import web
import requests
import json
import os
from aiohttp.web_response import Response
from aiohttp.web_request import Request
from requests.models import Response as reqResponse


TOKEN = '6148703501:AAHxM1XFR99QznDLb_BIptUOfGEeNFBK3RU'  # Токен телеграм бота
API_URL = f'https://api.telegram.org/bot{TOKEN}'  # адрес для отправки и получения команд
API_FILE_URL = f'https://api.telegram.org/file/bot{TOKEN}'  # адрес для получения файлов
BASE_URL = 'https://1354-95-73-105-75.eu.ngrok.io'  # адрес сайта
DIR = 'uploads'  # папка для сохранения файлов
COMMANDS = [  # команды бота
    {
        'command': 'start',
        'description': 'Старт бота'
    },
    {
        'command': 'send',
        'description': 'Записать и отправить аудиосообщение'
    },
    {
        'command': 'records',
        'description': 'Вывести список сообщений пользователя'
    },
]


async def get_file(data: dict[str, str]) -> dict[str, str] | None:
    """Получение информации о файле, отправленном юзером в бот."""
    method = f'{API_URL}/getFile'
    file = requests.post(method, data=data)
    if file.status_code != HTTPStatus.OK:
        return
    return json.loads(file._content)['result']


async def save_file(file_data: dict[str, str], chat_id: int) -> bool:
    """Сохранения файла, отправленного юзером в бот."""
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    path = file_data["file_path"]
    url = f'{API_FILE_URL}/{path}'
    file_name = f'{chat_id}-{file_data["file_unique_id"]}.{path[-3:]}'
    with open(f'{DIR}/{file_name}', "wb") as f:
        file = requests.get(url)
        if file.status_code != HTTPStatus.OK:
            return False
        try:
            f.write(file.content)
        except Exception:
            return False
    return True


async def records(chat_id: int) -> None:
    """Обработка команды /records."""
    pass


async def voice(data: dict[str, Union[str, int]], chat_id: int) -> None:
    """Обработка голосового сообщения, отправленного юзером в бот."""
    # if status_user != send:
    #     return
    message = {'chat_id': chat_id}
    duration = data['duration']
    file_id = data['file_id']
    file_size = data['file_size']
    file_data = await get_file({'file_id': file_id})
    if not file_data:
        message['text'] = 'Что-то пошло не так. Файл не сохранён'
        await send_message(message)
        return
    if await save_file(file_data, chat_id):
        # await save_to_db()
        message['text'] = 'Ваше сообщение принято'
    else:
        message['text'] = 'Что-то пошло не так. Повторите ещё раз'
    await send_message(message)


async def send(chat_id: int) -> None:
    """Обработка команды /start."""
    # await save_to_db() сохраняет состояние
    message = {
        'chat_id': chat_id,
        'text': 'Запишите и отправьте голосовое сообщение'
    }
    await send_message(message)


async def start(data: dict[str, Union[str, int, bool]], chat_id: int) -> None:
    """Обработка команды /start."""
    first_name = data['first_name']
    last_name = data['last_name']
    username = data['username']
    # await save_to_db()
    message = {
        'chat_id': chat_id,
        'text': (f'Приветствую вас, {first_name} {last_name}\n'
                 'Для отправки голосового сообщения отправьте команду /send')
    }
    await send_message(message)


async def ha_ha(chat_id: int) -> None:
    """Ответ на получение неизвестной информации."""
    message = {
        'chat_id': chat_id,
        'text': ('Ага, и вам приветик... '
                 'Отправьте /send для отправки голосового сообщения')
    }
    await send_message(message)


async def send_message(message: dict[str, str]) -> None | Response:
    """Отправка сообщения в бот."""
    headers = {'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(
                    f'{API_URL}/sendMessage',
                    data=json.dumps(message),
                    headers=headers) as resp:
            try:
                assert resp.status_code == HTTPStatus.OK
            except Exception:
                return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


async def handler(request: Request) -> Response:
    """Обработчик полученной от бота информации."""
    data = await request.json()
    chat_id = data['message']['from']['id']
    if data['message'].get('text'):
        match data['message']['text']:
            case "/start":
                await start(data['message']['from'], chat_id)
            case "/send":
                await send(chat_id)
            case "/records":
                await records(chat_id)
            case _:
                await ha_ha(chat_id)
    elif data['message'].get('voice'):
        await voice(data['message']['voice'], chat_id)
    else:
        await ha_ha(chat_id)
    return Response(status=HTTPStatus.OK)


def set_webhook() -> reqResponse:
    """Установка веб-хука бота."""
    method = f'{API_URL}/setWebhook'
    data = {'url': BASE_URL}
    return requests.post(method, data=data)


def set_commands() -> reqResponse:
    """Установка комманд бота."""
    method = f'{API_URL}/setMyCommands'
    commands = str(json.dumps(COMMANDS))
    send_text = f'{method}?commands={commands}'
    return requests.post(send_text)


if __name__ == '__main__':
    set_webhook = set_webhook()
    set_commands = set_commands()
    if (set_webhook.status_code == HTTPStatus.OK
            and set_commands.status_code == HTTPStatus.OK):
        app = web.Application()
        app.add_routes([web.get('/', handler), web.post('/', handler)])
        web.run_app(app)
    else:
        print('Вебхук не установлен')
