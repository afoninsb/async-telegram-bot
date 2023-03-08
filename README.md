# async-telegram-bot

Асинхронный Telegram-бот для передачи голосовых сообщений.

## Технологический стек

Python 3.10, aiohttp 3.8, asyncio 3.4, PostgreSQL 15.2, SQLAlchemy 2.0

## Создайте Telegram-бота

Создайте своего бота с помощью [@BotFather](https://t.me/BotFather)

## Настройка переменных окружения

Переименуйте файл _.env.dist_ в _.env_

Внесите в него _TOKEN_ вашего телеграм-бота:

```bash
TOKEN=61345445501:AAHxM1sjJljkhlkjhjIptUOfGEeNFBK3RU
```

## Локальный запуск

1) В папке проекта запустите терминал и отправьте команду:

```bash
sudo docker-compose up --build
```
2) Когда контейнеры запустятся, пройдите по адресу http://localhost:4551

3) Скопируйте на этой странице адрес _https_, выданный _ngrok_

4) Установите веб-хук бота, пройдя по адресу:

https://api.telegram.org/bot<_TOKEN_>/setWebhook?url=<_URL-NGROK_>,

где <_TOKEN_> - токен бота, выданный вам BotFather, <_URL-NGROK_> - https-url, скопированныйв п. 3

5) Можете проверять работу бота :)
