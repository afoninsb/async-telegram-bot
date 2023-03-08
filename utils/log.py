import logging


async def print_log(level, text) -> None:
    """Записываем логи."""
    if level == 'error':
        logging.error(text)
    else:
        logging.info(text)
