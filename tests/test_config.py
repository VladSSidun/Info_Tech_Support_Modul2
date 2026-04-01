# Тести для модуля конфігурації (app/core/config.py)

import pytest
from app.core.config import get, load_config


# ============================================================
# ТЕСТИ НОРМАЛЬНИХ УМОВ
# ============================================================

class TestNormalConditions:

    def test_load_config_returns_dict(self):
        """load_config() має повертати словник."""
        config = load_config()
        assert isinstance(config, dict)

    def test_get_app_name(self):
        """get() має повертати назву програми з конфігу."""
        name = get("app.name")
        assert name == "Project Risk AI"

    def test_get_app_version(self):
        """get() має повертати версію програми."""
        version = get("app.version")
        assert version is not None
        assert isinstance(version, str)

    def test_get_nested_key(self):
        """get() з вкладеним ключем через крапку → повертає правильне значення."""
        log_file = get("paths.log_file")
        assert log_file is not None
        assert "log" in log_file  # шлях має містити слово log


# ============================================================
# ТЕСТИ ГРАНИЧНИХ УМОВ
# ============================================================

class TestBoundaryConditions:

    def test_get_returns_default_for_missing_key(self):
        """get() для неіснуючого ключа → повертає default значення."""
        result = get("nonexistent.key", "default_value")
        assert result == "default_value"

    def test_get_returns_none_without_default(self):
        """get() без default для неіснуючого ключа → повертає None."""
        result = get("totally.fake.key")
        assert result is None

    def test_get_single_level_key(self):
        """get() з ключем без крапки → працює коректно."""
        config = load_config()
        first_key = list(config.keys())[0]  # беремо перший ключ верхнього рівня
        result = get(first_key)
        assert result is not None


# ============================================================
# ТЕСТИ ВИНЯТКОВИХ СИТУАЦІЙ
# ============================================================

class TestExceptionalConditions:

    def test_get_empty_string_key(self):
        """get() з порожнім рядком → не падає, повертає default."""
        result = get("", "fallback")
        assert result == "fallback"

    def test_get_deeply_nested_missing_key(self):
        """get() з дуже глибоким неіснуючим шляхом → повертає default."""
        result = get("a.b.c.d.e.f", 42)
        assert result == 42