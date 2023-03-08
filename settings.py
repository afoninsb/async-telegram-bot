import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# Телеграм бот токен
TOKEN = str(os.getenv('TOKEN'))

# адрес сайта
BASE_URL = str(os.getenv('BASE_URL'))

# адрес для отправки и получения команд
API_URL = f'https://api.telegram.org/bot{TOKEN}'

# адрес для получения файлов
API_FILE_URL = f'https://api.telegram.org/file/bot{TOKEN}'

# Настройки базы данных
DB = {
    'dbname': str(os.getenv('POSTGRES_DB')),
    'host': str(os.getenv('DB_HOST')),
    'user': str(os.getenv('POSTGRES_USER')),
    'password': str(os.getenv('POSTGRES_PASSWORD')),
    'port': int(os.getenv('DB_PORT'))
}

# папка для сохранения файлов
DIR = 'uploads'

# команды бота
COMMANDS = [
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
