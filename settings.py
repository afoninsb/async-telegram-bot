import os
from typing import Union

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings

load_dotenv(find_dotenv())


class Settings(BaseSettings):

    # Телеграм бот токен
    TOKEN: str = os.getenv('TOKEN')

    # адрес сайта
    BASE_URL: str = os.getenv('BASE_URL')

    # адрес для отправки и получения команд
    API_URL: str = f'https://api.telegram.org/bot{TOKEN}'

    # адрес для получения файлов
    API_FILE_URL: str = f'https://api.telegram.org/file/bot{TOKEN}'

    # Настройки базы данных
    DB: dict[str, Union[str, int]] = {
        'dbname': os.getenv('POSTGRES_DB'),
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'port': os.getenv('DB_PORT')
    }

    # папка для сохранения файлов
    DIR: str = 'uploads'

    # команды бота
    COMMANDS: list[dict[str, str]] = [
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
