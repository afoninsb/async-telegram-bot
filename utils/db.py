from typing import Union

from sqlalchemy.orm import Session, collections

import models


async def get_voice(voice_id: int) -> models.Voice:
    """Получаем информацию об аудиозаписи."""
    with Session(autoflush=False, bind=models.engine) as db:
        return db.query(models.Voice).filter(
            models.Voice.id == voice_id).first()


async def get_voices(chat_id: int) -> collections.InstrumentedList:
    """Получаем информацию об аудиозаписях пользователя."""
    with Session(autoflush=False, bind=models.engine) as db:
        user = db.query(models.User).filter(models.User.id == chat_id).first()
        return user.voices


async def save_voice(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о файле в базу данных."""
    chat_id = data.pop('user_id')
    with Session(autoflush=False, bind=models.engine) as db:
        user = db.query(models.User).filter(models.User.id == chat_id).first()
        voice = models.Voice(**data)
        user.voices.extend([voice])
        db.add(user)
        db.commit()


async def save_user(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о пользователе в базу данных."""
    with Session(autoflush=False, bind=models.engine) as db:
        user = models.User(**data)
        db.add(user)
        db.commit()


async def get_user(chat_id: int) -> models.User:
    """Получаем информацию о пользователе из базы данных."""
    with Session(autoflush=False, bind=models.engine) as db:
        return db.query(models.User).filter(models.User.id == chat_id).first()


async def edit_state_user(chat_id: int, state: str) -> None:
    """Изменяем состояние пользователя в базе данных."""
    user = await get_user(chat_id)
    with Session(autoflush=False, bind=models.engine) as db:
        user.state = state
        db.add(user)
        db.commit()