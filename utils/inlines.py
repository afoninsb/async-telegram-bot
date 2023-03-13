import json


async def voices_kbrd(voices) -> str:
    """Кнопки аудиозаписей пользователя."""
    inline_buttons = [0] * len(voices)
    for id, voice in enumerate(voices):
        inline_buttons[id] = [{
            'text': f'Запись #{id + 1}',
            'callback_data': f'voice:{voice["id"]}'
        }]
    kbrd = {'inline_keyboard': inline_buttons}
    return json.dumps(kbrd)
