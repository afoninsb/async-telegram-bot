class NoData(Exception):
    """Пустой словарь от бота."""

    __slots__ = ('message',)


class MessageNotSent(Exception):
    """Сообщение не отправлено."""

    __slots__ = ('message',)


class DBError(Exception):
    """Обшибка при работе с базой данных."""

    __slots__ = ('message',)


class FileNotGet(Exception):
    """Файл не скачан с сервера Телеграм."""

    __slots__ = ('message',)


class FileNotSave(Exception):
    """Файл не сохранен на диск."""

    __slots__ = ('message',)
