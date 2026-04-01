# Тести для ML модуля (app/ml/model.py)

import pytest
import os
import pandas as pd
from app.ml.model import generate_training_data, train_model, predict, load_model
from app.ml.features import get_feature_keys, RISK_LABELS


# Тестові вхідні дані — типовий "небезпечний" проєкт
HIGH_RISK_INPUT = {
    "team_size": 2,
    "team_experience": 0.5,
    "budget": 10.0,
    "duration_weeks": 100,
    "requirements_count": 490,
    "requirements_clarity": 0.05,
    "stakeholders_count": 19,
    "has_risk_manager": 0,
}

# Типовий "безпечний" проєкт
LOW_RISK_INPUT = {
    "team_size": 45,
    "team_experience": 18.0,
    "budget": 9000.0,
    "duration_weeks": 4,
    "requirements_count": 10,
    "requirements_clarity": 0.95,
    "stakeholders_count": 2,
    "has_risk_manager": 1,
}


# ============================================================
# ТЕСТИ НОРМАЛЬНИХ УМОВ
# ============================================================

class TestNormalConditions:

    def test_generate_data_returns_dataframe(self):
        """generate_training_data() має повертати DataFrame."""
        df = generate_training_data(100)
        assert isinstance(df, pd.DataFrame)

    def test_generate_data_correct_columns(self):
        """DataFrame має містити всі колонки параметрів + risk_level."""
        df = generate_training_data(100)
        expected_cols = get_feature_keys() + ["risk_level"]
        for col in expected_cols:
            assert col in df.columns, f"Колонка {col} відсутня"

    def test_generate_data_correct_row_count(self):
        """Кількість рядків має відповідати переданому n_samples."""
        df = generate_training_data(200)
        assert len(df) == 200

    def test_train_model_returns_tuple(self):
        """train_model() має повертати tuple з трьох елементів."""
        result = train_model()
        assert isinstance(result, tuple)
        assert len(result) == 3  # (model, accuracy, report)

    def test_train_model_accuracy_reasonable(self):
        """Точність моделі має бути в розумних межах (50%–100%)."""
        _, accuracy, _ = train_model()
        assert 0.5 <= accuracy <= 1.0

    def test_predict_returns_valid_risk_level(self):
        """predict() має повертати рівень ризику 0, 1 або 2."""
        model, _, _ = train_model()
        result = predict(model, HIGH_RISK_INPUT)
        assert result["risk_level"] in [0, 1, 2]

    def test_predict_returns_valid_label(self):
        """predict() має повертати одну з трьох міток ризику."""
        model, _, _ = train_model()
        result = predict(model, LOW_RISK_INPUT)
        assert result["risk_label"] in RISK_LABELS.values()

    def test_predict_probabilities_sum_to_one(self):
        """Сума ймовірностей всіх класів має дорівнювати 1.0."""
        model, _, _ = train_model()
        result = predict(model, HIGH_RISK_INPUT)
        total = sum(result["probabilities"].values())
        # Використовуємо pytest.approx бо float арифметика не ідеальна
        # наприклад: 0.1 + 0.2 = 0.30000000000000004 а не 0.3
        assert total == pytest.approx(1.0, abs=0.01)

    def test_predict_feature_importance_keys(self):
        """feature_importance має містити всі ключі параметрів."""
        model, _, _ = train_model()
        result = predict(model, HIGH_RISK_INPUT)
        for key in get_feature_keys():
            assert key in result["feature_importance"]


# ============================================================
# ТЕСТИ ГРАНИЧНИХ УМОВ
# ============================================================

class TestBoundaryConditions:

    def test_generate_minimum_samples(self):
        """Генерація мінімальної кількості зразків (10) → не падає."""
        df = generate_training_data(10)
        assert len(df) == 10

    def test_predict_high_risk_project(self):
        """Проєкт з найгіршими параметрами → очікується Високий ризик."""
        model, _, _ = train_model()
        result = predict(model, HIGH_RISK_INPUT)
        # Перевіряємо що Високий ризик є найімовірнішим класом
        max_prob_label = max(
            result["probabilities"],
            key=result["probabilities"].get
        )
        assert max_prob_label == "Високий"

    def test_predict_low_risk_project(self):
        """Проєкт з найкращими параметрами → очікується Низький ризик."""
        model, _, _ = train_model()
        result = predict(model, LOW_RISK_INPUT)
        max_prob_label = max(
            result["probabilities"],
            key=result["probabilities"].get
        )
        assert max_prob_label == "Низький"

    def test_risk_level_values_in_range(self):
        """Всі згенеровані рівні ризику мають бути 0, 1 або 2."""
        df = generate_training_data(100)
        assert df["risk_level"].isin([0, 1, 2]).all()


# ============================================================
# ТЕСТИ ВИНЯТКОВИХ СИТУАЦІЙ
# ============================================================

class TestExceptionalConditions:

    def test_predict_missing_key_raises_error(self):
        """predict() з неповними даними → має кинути KeyError."""
        model, _, _ = train_model()
        incomplete_data = {"team_size": 5}  # тільки один параметр
        with pytest.raises((KeyError, Exception)):
            predict(model, incomplete_data)

    def test_load_model_creates_if_not_exists(self, tmp_path, monkeypatch):
        """load_model() якщо файл не існує → навчає нову модель автоматично."""
        # monkeypatch тимчасово замінює значення конфігу для цього тесту
        # tmp_path — тимчасова папка яку pytest створює і видаляє автоматично
        fake_path = str(tmp_path / "nonexistent.pkl")
        monkeypatch.setattr(
            "app.ml.model.get",
            lambda key, default=None: fake_path if key == "paths.model_file" else default
        )
        model = load_model()
        assert model is not None