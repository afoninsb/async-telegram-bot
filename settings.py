import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

TOKEN = str(os.getenv('TOKEN'))  # Телеграм бот токен

BASE_URL = str(os.getenv('BASE_URL'))  # адрес сайта

API_URL = f'https://api.telegram.org/bot{TOKEN}'  # адрес для отправки и получения команд

API_FILE_URL = f'https://api.telegram.org/file/bot{TOKEN}'  # адрес для получения файлов

DB = {
    'dbname': str(os.getenv('POSTGRES_DB')),
    'host': str(os.getenv('DB_HOST')),
    'user': str(os.getenv('POSTGRES_USER')),
    'password': str(os.getenv('POSTGRES_PASSWORD')),
    'port': int(os.getenv('DB_PORT'))
}

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
