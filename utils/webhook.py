import json

import requests
from requests.models import Response as reqResponse

import settings


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
