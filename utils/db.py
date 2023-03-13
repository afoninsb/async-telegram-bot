import asyncpg
from typing import Union

from exceptions import DBError
from settings import settings
from utils.log import print_log


async def connection():
    try:
        return await asyncpg.connect(
            host=settings.DB['host'],
            port=settings.DB['port'],
            user=settings.DB['user'],
            database=settings.DB['dbname'],
            password=settings.DB['password']
        )
    except asyncpg.exceptions as e:
        raise DBError(f'ОШИБКА подключения к базе данных: {e}') from e


async def get_voice(voice_id: int) -> asyncpg.Record:
    """Получаем информацию об аудиозаписи."""
    conn = await connection()
    sql = f"SELECT * FROM voices WHERE id = {voice_id}"
    try:
        return await conn.fetchrow(sql)
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении информации из БД о файле {voice_id}') from e
    finally:
        await conn.close()


async def get_voices(chat_id: int) -> list[Union[str, int]]:
    """Получаем информацию об аудиозаписях пользователя."""
    conn = await connection()
    sql = f"SELECT * FROM voices WHERE user_id = {chat_id}"
    try:
        return await conn.fetch(sql)
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении списка файлов из базы данных') from e
    finally:
        await conn.close()


async def save_voice(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о файле в базу данных."""
    conn = await connection()
    sql = ("INSERT INTO voices (user_id, file_id, file_size, duration, url) "
           f"VALUES ({data['user_id']}, '{data['file_id']}', "
           f"{data['file_size']}, {data['duration']}, '{data['url']}')")
    try:
        await conn.execute(sql)
        await print_log('info', 'В БД создана запись аудиозаписи')
    except Exception as e:
        raise DBError(
            'ОШИБКА при внесении информации о файле в базу данных') from e
    finally:
        await conn.close()


async def save_user(data: dict[str, Union[str, int]]) -> None:
    """Сохраняем информацию о пользователе в базу данных."""
    conn = await connection()
    sql = ("INSERT INTO users (id, first_name, last_name, username) "
           f"VALUES ({data['id']}, '{data['first_name']}', "
           f"'{data['last_name']}', '{data['username']}')")
    try:
        await conn.execute(sql)
        await print_log(
            'info',
            f"В БД создана запись пользователя {data['id']}"
        )
    except Exception as e:
        raise DBError(
            'ОШИБКА при внесении информации о пользователе в базу данных'
        ) from e
    finally:
        await conn.close()


async def get_user(chat_id: int) -> asyncpg.Record:
    """Получаем информацию о пользователе из базы данных."""
    conn = await connection()
    sql = f"SELECT * FROM users WHERE id = {chat_id}"
    try:
        return await conn.fetchrow(sql)
    except Exception as e:
        raise DBError(
            'ОШИБКА при получении информации о пользователе из базы данных'
        ) from e
    finally:
        await conn.close()


async def edit_state_user(chat_id: int, state: str) -> None:
    """Изменяем состояние пользователя в базе данных."""
    conn = await connection()
    sql = f"UPDATE users SET state = '{state}' WHERE id = {chat_id}"
    try:
        await conn.execute(sql)
    except Exception as e:
        raise DBError(
            'ОШИБКА при изменении состояния пользователя в базе данных'
        )from e
    finally:
        await conn.close()
