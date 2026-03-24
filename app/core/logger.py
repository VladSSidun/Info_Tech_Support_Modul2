# app/core/logger.py
# Налаштування логування — пише в файл і термінал одночасно

import logging
import os
from app.core.config import get


def setup_logger() -> logging.Logger:
    """
    Створює головний логер програми.
    Логи йдуть одночасно в logs/app.log і термінал.
    """
    log_file = get("paths.log_file", "logs/app.log")
    log_dir = os.path.dirname(log_file)

    # Створюємо папку logs/ якщо не існує
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logger = logging.getLogger("ProjectRiskAI")
    logger.setLevel(logging.DEBUG)

    # Уникаємо дублювання якщо logger вже створений
    if logger.handlers:
        return logger

    # Handler 1: запис у файл
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Handler 2: вивід у термінал
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Логер ініціалізовано успішно")
    return logger


# Глобальний логер — інші модулі імпортують його так:
# from app.core.logger import logger
logger = setup_logger()