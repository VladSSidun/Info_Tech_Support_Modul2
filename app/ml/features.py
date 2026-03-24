# app/ml/features.py
# Опис вхідних параметрів моделі оцінки ризику проєкту

# Список всіх параметрів які вводить користувач
# Кожен параметр — словник з описом для GUI та валідації
FEATURES = [
    {
        "key": "team_size",
        "label": "Кількість учасників команди",
        "type": "int",
        "min": 1,
        "max": 50,
        "default": 5,
        "hint": "Введіть кількість людей у команді (1–50)"
    },
    {
        "key": "team_experience",
        "label": "Досвід команди (роки)",
        "type": "float",
        "min": 0.0,
        "max": 20.0,
        "default": 2.0,
        "hint": "Середній досвід учасників у роках (0–20)"
    },
    {
        "key": "budget",
        "label": "Бюджет проєкту (тис. грн)",
        "type": "float",
        "min": 10.0,
        "max": 10000.0,
        "default": 500.0,
        "hint": "Загальний бюджет проєкту в тисячах гривень (10–10000)"
    },
    {
        "key": "duration_weeks",
        "label": "Тривалість проєкту (тижні)",
        "type": "int",
        "min": 1,
        "max": 104,
        "default": 12,
        "hint": "Планована тривалість проєкту в тижнях (1–104)"
    },
    {
        "key": "requirements_count",
        "label": "Кількість вимог",
        "type": "int",
        "min": 1,
        "max": 500,
        "default": 30,
        "hint": "Загальна кількість функціональних вимог (1–500)"
    },
    {
        "key": "requirements_clarity",
        "label": "Чіткість вимог (0–1)",
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "default": 0.7,
        "hint": "Наскільки чіткі вимоги: 0 = повна невизначеність, 1 = повна ясність"
    },
    {
        "key": "stakeholders_count",
        "label": "Кількість стейкхолдерів",
        "type": "int",
        "min": 1,
        "max": 20,
        "default": 3,
        "hint": "Кількість зацікавлених сторін проєкту (1–20)"
    },
    {
        "key": "has_risk_manager",
        "label": "Наявність ризик-менеджера",
        "type": "bool",
        "min": 0,
        "max": 1,
        "default": 0,
        "hint": "Чи є в команді відповідальний за управління ризиками?"
    },
]

# Назви рівнів ризику — використовуються в GUI і звіті
RISK_LABELS = {
    0: "Низький",
    1: "Середній",
    2: "Високий"
}

# Кольори для відображення рівня ризику в GUI
RISK_COLORS = {
    0: "#2ecc71",   # зелений
    1: "#f39c12",   # помаранчевий
    2: "#e74c3c"    # червоний
}


def validate_input(key: str, value: str) -> tuple[bool, str, float | int | None]:
    """
    Валідує введене користувачем значення для конкретного параметра.

    Повертає tuple з трьох елементів:
        (is_valid, error_message, converted_value)

    Приклади:
        validate_input("team_size", "5")   -> (True, "", 5)
        validate_input("team_size", "abc") -> (False, "Введіть ціле число", None)
        validate_input("team_size", "999") -> (False, "Значення має бути від 1 до 50", None)
    """
    # Знаходимо опис параметра за ключем
    feature = next((f for f in FEATURES if f["key"] == key), None)

    if feature is None:
        return False, f"Невідомий параметр: {key}", None

    # Перевірка на порожнє поле
    if value.strip() == "":
        return False, "Поле не може бути порожнім", None

    # Перевірка типу і конвертація
    try:
        if feature["type"] == "int":
            converted = int(value)
        elif feature["type"] == "float":
            converted = float(value.replace(",", "."))  # підтримка коми як роздільника
        elif feature["type"] == "bool":
            converted = int(value)
            if converted not in (0, 1):
                return False, "Введіть 0 або 1", None
        else:
            converted = float(value)
    except ValueError:
        if feature["type"] == "int":
            return False, "Введіть ціле число", None
        else:
            return False, "Введіть числове значення", None

    # Перевірка діапазону
    if converted < feature["min"] or converted > feature["max"]:
        return False, f"Значення має бути від {feature['min']} до {feature['max']}", None

    return True, "", converted


def get_feature_keys() -> list[str]:
    """Повертає список ключів всіх параметрів — для формування масиву даних."""
    return [f["key"] for f in FEATURES]