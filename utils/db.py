from typing import Union

from sqlalchemy.orm import Session, collections

import models
from exceptions import DBError
from utils.log import print_log


async def get_voice(voice_id: int) -> models.Voice:
    """Получаем информацию об аудиозаписи."""
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            return db.query(models.Voice).filter(
                models.Voice.id == voice_id).first()
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении информации из БД о файле {voice_id}') from e


async def get_voices(chat_id: int) -> collections.InstrumentedList:
    """Получаем информацию об аудиозаписях пользователя."""
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            user = db.query(models.User).filter(
                models.User.id == chat_id).first()
            return user.voices
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении списка файлов из базы данных') from e


async def save_voice(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о файле в базу данных."""
    chat_id = data.pop('user_id')
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            user = db.query(models.User).filter(
                models.User.id == chat_id).first()
            voice = models.Voice(**data)
            user.voices.extend([voice])
            db.add(user)
            db.commit()
            await print_log(
                'info',
                f'В БД создана запись аудиозаписи {voice.id}'
            )
    except Exception as e:
        raise DBError(
            'ОШИБКА при внесении информации о файле в базу данных') from e


async def save_user(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о пользователе в базу данных."""
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            user = models.User(**data)
            db.add(user)
            db.commit()
            await print_log(
                'info',
                f'В БД создана запись пользователя {user.id}'
            )
    except Exception as e:
        raise DBError(
            'ОШИБКА при внесении информации о пользователе в базу данных'
        ) from e


async def get_user(chat_id: int) -> models.User:
    """Получаем информацию о пользователе из базы данных."""
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            return db.query(models.User).filter(
                models.User.id == chat_id).first()
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении информации о пользователе из базы данных'
        ) from e


async def edit_state_user(chat_id: int, state: str) -> None:
    """Изменяем состояние пользователя в базе данных."""
    user = await get_user(chat_id)
    try:
        with Session(autoflush=False, bind=models.engine) as db:
            user.state = state
            db.add(user)
            db.commit()
    except Exception as e:
        raise DBError(
            'ОШИБКА при изменении состояния пользователя в базе данных'
        )from e
