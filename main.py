# main.py
# Точка входу програми — запускає головне вікно

import sys
import os

# Додаємо корінь проєкту до шляху пошуку модулів
# Це потрібно щоб імпорти типу "from app.core..." працювали коректно
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.logger import logger
from app.core.config import get
from app.gui.main_window import MainWindow


def main():
    """Головна функція запуску програми."""
    app_name = get("app.name", "Project Risk AI")
    version = get("app.version", "1.0.0")

    logger.info(f"Запуск програми {app_name} v{version}")

    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.error(f"Критична помилка: {e}", exc_info=True)
        raise
    finally:
        logger.info("Програму завершено")


if __name__ == "__main__":
    main()