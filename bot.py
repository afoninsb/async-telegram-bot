import asyncio
from http import HTTPStatus
from typing import Union
import aiohttp
from aiohttp import web
import psycopg2
import requests
import json
import os
from aiohttp.web_response import Response
from aiohttp.web_request import Request
from requests.models import Response as reqResponse
from sqlalchemy.orm import Session

import models
import settings


async def save_voice(data: dict[str, Union[str, int]]):
    with Session(autoflush=False, bind=models.engine) as db:
        voice = models.Voice(**data)
        db.add(voice)
        db.commit()


async def save_user(data: dict[str, Union[str, int]]):
    with Session(autoflush=False, bind=models.engine) as db:
        user = models.User(**data)
        db.add(user)
        db.commit()


async def get_user(chat_id: int) -> models.User:
    with Session(autoflush=False, bind=models.engine) as db:
        return db.query(models.User).filter(models.User.id == chat_id).first()


async def edit_state_user(chat_id: int, state: str) -> None:
    user = await get_user(chat_id)
    with Session(autoflush=False, bind=models.engine) as db:
        user.state = state
        db.add(user)
        db.commit()


async def get_file(data: dict[str, str]) -> dict[str, str] | None:
    """Получение информации о файле, отправленном юзером в бот."""
    method = f'{settings.API_URL}/getFile'
    file = requests.post(method, data=data)
    if file.status_code != HTTPStatus.OK:
        return
    return json.loads(file._content)['result']


async def save_file(file_data: dict[str, str], chat_id: int) -> str | None:
    """Сохранения файла, отправленного юзером в бот."""
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


async def records(chat_id: int) -> None:
    """Обработка команды /records."""
    pass


async def voice(data: dict[str, Union[str, int]], chat_id: int) -> None:
    """Обработка голосового сообщения, отправленного юзером в бот."""
    user = await get_user(chat_id)
    if user.state != 'send':
        message = {
            'chat_id': chat_id,
            'text': 'Для отправки голосового сообщения отправьте команду /send'
        }
        await send_message(message)
        return
    await edit_state_user(chat_id, '')
    message = {'chat_id': chat_id}
    duration = data['duration']
    file_id = data['file_id']
    file_size = data['file_size']
    file_data = await get_file({'file_id': file_id})
    if not file_data:
        message['text'] = 'Что-то пошло не так. Файл не сохранён'
        await send_message(message)
        return
    file_name = await save_file(file_data, chat_id)
    if not file_name:
        message['text'] = 'Что-то пошло не так. Повторите ещё раз'
        await send_message(message)
        return
    await save_voice({
        'user_id': chat_id,
        'file_id': file_id,
        'file_size': file_size,
        'duration': duration,
        'url': f'{settings.DIR}/{file_name}',
    })
    message['text'] = 'Ваше сообщение принято'
    await send_message(message)


async def send(chat_id: int) -> None:
    """Обработка команды /start."""
    await edit_state_user(chat_id, 'send')
    message = {
        'chat_id': chat_id,
        'text': 'Запишите и отправьте голосовое сообщение'
    }
    await send_message(message)


async def start(data: dict[str, Union[str, int, bool]], chat_id: int) -> None:
    """Обработка команды /start."""
    user = await get_user(chat_id)
    if user:
        message = {
            'chat_id': chat_id,
            'text': 'Вы уже зарегистрированы'
        }
        await send_message(message)
        return
    first_name = data['first_name']
    last_name = data['last_name']
    username = data['username']
    await save_user({
        'id': chat_id,
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
    })
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
        'text': ('Ага, и вам приветик...\n'
                 'Отправьте /send для отправки голосового сообщения')
    }
    await send_message(message)


async def send_message(message: dict[str, str]) -> None | Response:
    """Отправка сообщения в бот."""
    headers = {'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(
                    f'{settings.API_URL}/sendMessage',
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
            case '/start':
                await start(data['message']['from'], chat_id)
            case '/send':
                await send(chat_id)
            case '/records':
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
    method = f'{settings.API_URL}/setWebhook'
    data = {'url': settings.BASE_URL}
    return requests.post(method, data=data)


def set_commands() -> reqResponse:
    """Установка комманд бота."""
    method = f'{settings.API_URL}/setMyCommands'
    commands = str(json.dumps(settings.COMMANDS))
    send_text = f'{method}?commands={commands}'
    return requests.post(send_text)


if __name__ == '__main__':
    try:
        connect = psycopg2.connect(**settings.DB)
    except psycopg2.OperationalError:
        print("Не удалось подключиться к базе данных")
        raise
    connect.autocommit = True
    set_webhook = set_webhook()
    set_commands = set_commands()
    if (set_webhook.status_code == HTTPStatus.OK
            and set_commands.status_code == HTTPStatus.OK):
        app = web.Application()
        app.add_routes([web.get('/', handler), web.post('/', handler)])
        web.run_app(app)
    else:
        print('Вебхук не установлен')
