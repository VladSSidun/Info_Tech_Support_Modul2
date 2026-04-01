# Тести для модуля валідації вхідних параметрів (app/ml/features.py)

import pytest
from app.ml.features import validate_input, get_feature_keys, FEATURES


# ============================================================
# ТЕСТИ НОРМАЛЬНИХ УМОВ
# Перевіряємо типові коректні сценарії — програма має працювати
# ============================================================

class TestNormalConditions:

    def test_valid_integer_field(self):
        """Ціле число в допустимому діапазоні → має повернути True і конвертоване значення."""
        is_valid, error, value = validate_input("team_size", "10")
        assert is_valid is True
        assert error == ""
        assert value == 10
        assert isinstance(value, int)  # перевіряємо що саме int, не float

    def test_valid_float_field(self):
        """Дробове число в допустимому діапазоні → має повернути True і float."""
        is_valid, error, value = validate_input("team_experience", "5.5")
        assert is_valid is True
        assert value == 5.5
        assert isinstance(value, float)

    def test_valid_bool_field_zero(self):
        """Булеве поле зі значенням 0 → коректне."""
        is_valid, error, value = validate_input("has_risk_manager", "0")
        assert is_valid is True
        assert value == 0

    def test_valid_bool_field_one(self):
        """Булеве поле зі значенням 1 → коректне."""
        is_valid, error, value = validate_input("has_risk_manager", "1")
        assert is_valid is True
        assert value == 1

    def test_comma_as_decimal_separator(self):
        """Кома як роздільник дробової частини → має прийматись як коректне значення."""
        # Користувачі часто вводять 5,5 замість 5.5 — ми це підтримуємо
        is_valid, error, value = validate_input("team_experience", "5,5")
        assert is_valid is True
        assert value == 5.5

    def test_all_feature_keys_present(self):
        """Список ключів параметрів має містити всі 8 параметрів моделі."""
        keys = get_feature_keys()
        assert len(keys) == 8
        assert "team_size" in keys
        assert "has_risk_manager" in keys


# ============================================================
# ТЕСТИ ГРАНИЧНИХ УМОВ
# Перевіряємо мінімальні та максимальні допустимі значення
# ============================================================

class TestBoundaryConditions:

    def test_minimum_team_size(self):
        """Мінімальне значення team_size = 1 → має бути коректним."""
        is_valid, error, value = validate_input("team_size", "1")
        assert is_valid is True
        assert value == 1

    def test_maximum_team_size(self):
        """Максимальне значення team_size = 50 → має бути коректним."""
        is_valid, error, value = validate_input("team_size", "50")
        assert is_valid is True
        assert value == 50

    def test_minimum_requirements_clarity(self):
        """Мінімальне значення чіткості вимог = 0.0 → коректне."""
        is_valid, error, value = validate_input("requirements_clarity", "0.0")
        assert is_valid is True
        assert value == 0.0

    def test_maximum_requirements_clarity(self):
        """Максимальне значення чіткості вимог = 1.0 → коректне."""
        is_valid, error, value = validate_input("requirements_clarity", "1.0")
        assert is_valid is True
        assert value == 1.0

    def test_just_above_maximum(self):
        """Значення на 1 більше за максимум → має повернути помилку."""
        is_valid, error, value = validate_input("team_size", "51")
        assert is_valid is False
        assert value is None
        assert "50" in error  # повідомлення має містити максимальне значення

    def test_just_below_minimum(self):
        """Значення на 1 менше за мінімум → має повернути помилку."""
        is_valid, error, value = validate_input("team_size", "0")
        assert is_valid is False
        assert value is None

    def test_maximum_budget(self):
        """Максимальний бюджет = 10000.0 → коректне."""
        is_valid, error, value = validate_input("budget", "10000.0")
        assert is_valid is True
        assert value == 10000.0

    def test_minimum_budget(self):
        """Мінімальний бюджет = 10.0 → коректне."""
        is_valid, error, value = validate_input("budget", "10.0")
        assert is_valid is True
        assert value == 10.0


# ============================================================
# ТЕСТИ ВИНЯТКОВИХ СИТУАЦІЙ
# Перевіряємо некоректний ввід — програма не має падати
# ============================================================

class TestExceptionalConditions:

    def test_empty_string(self):
        """Порожнє поле → повідомлення про помилку, не виняток."""
        is_valid, error, value = validate_input("team_size", "")
        assert is_valid is False
        assert value is None
        assert error != ""  # повідомлення про помилку має бути не порожнім

    def test_text_instead_of_number(self):
        """Текст замість числа → повідомлення про помилку."""
        is_valid, error, value = validate_input("team_size", "abc")
        assert is_valid is False
        assert value is None

    def test_special_characters(self):
        """Спеціальні символи → повідомлення про помилку."""
        is_valid, error, value = validate_input("budget", "!@#$")
        assert is_valid is False
        assert value is None

    def test_negative_value(self):
        """Від'ємне значення → поза допустимим діапазоном."""
        is_valid, error, value = validate_input("team_size", "-5")
        assert is_valid is False
        assert value is None

    def test_float_for_integer_field(self):
        """Дробове число для поля типу int → має повернути помилку."""
        is_valid, error, value = validate_input("team_size", "5.5")
        assert is_valid is False

    def test_bool_field_invalid_value(self):
        """Значення 2 для булевого поля → тільки 0 або 1 допустимі."""
        is_valid, error, value = validate_input("has_risk_manager", "2")
        assert is_valid is False
        assert value is None

    def test_unknown_feature_key(self):
        """Невідомий ключ параметра → повертає False без виключення."""
        is_valid, error, value = validate_input("unknown_field", "5")
        assert is_valid is False
        assert value is None

    def test_whitespace_only(self):
        """Рядок з пробілів → вважається порожнім полем."""
        is_valid, error, value = validate_input("team_size", "   ")
        assert is_valid is False
        assert value is None