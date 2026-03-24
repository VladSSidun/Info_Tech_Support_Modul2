# app/core/config.py
# Модуль для роботи з конфігураційним файлом програми

import json
import os

# Шлях до config.json — відносно цього файлу піднімаємось на 2 рівні вгору
CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "config.json"
)


def load_config() -> dict:
    """Завантажує конфігурацію з config.json."""
    config_path = os.path.abspath(CONFIG_PATH)

    if not os.path.exists(config_path):
        print(f"[WARNING] config.json не знайдено: {config_path}")
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """Зберігає оновлену конфігурацію назад у config.json."""
    config_path = os.path.abspath(CONFIG_PATH)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get(key_path: str, default=None):
    """
    Отримує значення з конфігу по точковому шляху.

    Приклади:
        get("app.version")    -> "1.0.0"
        get("paths.log_file") -> "logs/app.log"
        get("app.missing", 0) -> 0
    """
    config = load_config()
    keys = key_path.split(".")  # "app.version" -> ["app", "version"]

    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value