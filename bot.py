import json
import logging
from http import HTTPStatus
from typing import Union

import aiohttp
import psycopg2
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

import models
from exceptions import DBError, FileNotGet, FileNotSave, MessageNotSent, NoData
from settings import Settings
from utils import (edit_state_user, get_file, get_user, get_voice, get_voices,
                   print_log, save_file, save_user, save_voice, set_commands,
                   set_webhook, voices_kbrd)

settings = Settings()


async def voice_info(data: str, chat_id: int) -> models.Voice:
    """Отправляем информацию об аудиозаписи."""
    voice_id = int(data.split(':')[1])
    voice = await get_voice(voice_id)
    text = (f'Информация о файле:\n'
            f'file_size: {voice.file_size} байт\n'
            f'duration: {voice.duration} сек')
    message = {
        'chat_id': chat_id,
        'text': text,
    }
    await send_message(message)


async def records(chat_id: int) -> None:
    """Обработка команды /records."""
    voices = await get_voices(chat_id)
    keyboard = await voices_kbrd(voices)
    message = {
        'chat_id': chat_id,
        'text': 'Ваши записи:',
        'reply_markup': keyboard,
    }
    await send_message(message)


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
    """Обработка команды /send."""
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
            except Exception as e:
                raise MessageNotSent('Сообщение не отправлено') from e


async def get_message(
    data: dict[str, Union[str, int, bool]]
) -> dict[str, Union[str, int, bool]] | None:
    """Поолучаем объект message с веб-хука."""
    if data.get('message'):
        return data['message']
    if data.get('callback_query'):
        return data['callback_query']['message']
    raise NoData('Получен пустой словарь')


async def handler(request: Request) -> Response:
    """Обработчик полученной от бота информации."""
    data = await request.json()
    try:
        message = await get_message(data)
        chat_id = message['chat']['id']
        if data.get('callback_query'):
            await voice_info(data['callback_query']['data'], chat_id)
        elif data['message'].get('text'):
            match message['text']:
                case '/start':
                    await start(data['message']['from'], chat_id)
                case '/send':
                    await send(chat_id)
                case '/records':
                    await records(chat_id)
                case _:
                    await ha_ha(chat_id)
        elif message.get('voice'):
            await voice(data['message']['voice'], chat_id)
        else:
            await ha_ha(chat_id)
    except (NoData, MessageNotSent, DBError, FileNotGet, FileNotSave) as exc:
        await print_log('error', exc)
    else:
        return Response(status=HTTPStatus.OK)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='log.log',
        filemode='w',
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
    )

    try:
        connect = psycopg2.connect(**settings.DB)
    except psycopg2.OperationalError:
        print("Не удалось подключиться к базе данных")
        logging.error('Вебхук не установлен')
        raise
    webhook = set_webhook()
    commands = set_commands()
    if (webhook.status_code == HTTPStatus.OK
            and commands.status_code == HTTPStatus.OK):
        app = web.Application()
        app.add_routes([web.get('/', handler), web.post('/', handler)])
        web.run_app(app)
    else:
        print('Вебхук не установлен')
        logging.error('Вебхук не установлен')
