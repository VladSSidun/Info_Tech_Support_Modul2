# tests/test_report.py
# Тести для модуля генерації звітів (app/ml/report.py)

import pytest
import os
import openpyxl
from unittest.mock import patch
from app.ml.report import generate_report, export_json
from app.ml.model import train_model, predict


SAMPLE_INPUT = {
    "team_size": 5,
    "team_experience": 2.0,
    "budget": 500.0,
    "duration_weeks": 12,
    "requirements_count": 30,
    "requirements_clarity": 0.7,
    "stakeholders_count": 3,
    "has_risk_manager": 0,
}


@pytest.fixture(scope="module")
def sample_result():
    """Навчає модель один раз і повертає результат передбачення."""
    model, _, _ = train_model()
    return predict(model, SAMPLE_INPUT)


@pytest.fixture
def report_path(sample_result, tmp_path, monkeypatch):
    """
    Генерує звіт у тимчасову папку tmp_path.
    tmp_path — вбудована fixture pytest, створює унікальну тимчасову
    папку для кожного тесту і автоматично видаляє її після.
    Так уникаємо PermissionError на Windows.
    """
    # Підміняємо шлях до папки звітів на тимчасову папку
    monkeypatch.setattr(
        "app.ml.report.get",
        lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
    )
    filepath = generate_report(SAMPLE_INPUT, sample_result)
    return filepath


# ============================================================
# ТЕСТИ НОРМАЛЬНИХ УМОВ
# ============================================================

class TestNormalConditions:

    def test_report_file_created(self, report_path):
        """generate_report() має створити файл на диску."""
        assert os.path.exists(report_path)

    def test_report_has_xlsx_extension(self, report_path):
        """Файл звіту має мати розширення .xlsx."""
        assert report_path.endswith(".xlsx")

    def test_report_is_valid_excel(self, report_path):
        """Згенерований файл має відкриватись як валідний Excel."""
        wb = openpyxl.load_workbook(report_path)
        assert wb is not None
        wb.close()

    def test_report_contains_risk_label(self, report_path, sample_result):
        """Звіт має містити мітку рівня ризику в клітинках."""
        wb = openpyxl.load_workbook(report_path)
        ws = wb.active

        all_values = []
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    all_values.append(str(cell.value))
        wb.close()

        assert sample_result["risk_label"] in all_values


# ============================================================
# ТЕСТИ ГРАНИЧНИХ УМОВ
# ============================================================

class TestBoundaryConditions:

    def test_report_unique_filenames(self, sample_result, tmp_path, monkeypatch):
        """Два звіти підряд мають мати різні імена файлів."""
        import time

        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )

        path1 = generate_report(SAMPLE_INPUT, sample_result)
        time.sleep(1)
        path2 = generate_report(SAMPLE_INPUT, sample_result)

        assert path1 != path2


# ============================================================
# ТЕСТИ ВИНЯТКОВИХ СИТУАЦІЙ
# ============================================================

class TestExceptionalConditions:

    def test_report_with_empty_input(self, sample_result, tmp_path, monkeypatch):
        """generate_report() з порожніми input_data → не падає, файл створюється."""
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        try:
            filepath = generate_report({}, sample_result)
            assert os.path.exists(filepath)
        except Exception as e:
            pytest.fail(f"generate_report() кинув виняток з порожніми даними: {e}")



# ============================================================
# ТЕСТИ НОВОГО МОДУЛЯ: export_json() — Частина 4
# ============================================================

class TestJsonExport:
    """Тести для функції export_json() — новий функціонал v1.1.0"""

    # Тест нормальних умов 1
    def test_json_file_created(self, sample_result, tmp_path, monkeypatch):
        """export_json() має створити .json файл на диску."""
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = export_json(SAMPLE_INPUT, sample_result)
        assert os.path.exists(filepath), "JSON файл не створено"

    # Тест нормальних умов 2
    def test_json_file_valid(self, sample_result, tmp_path, monkeypatch):
        """Створений файл має бути валідним JSON."""
        import json
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = export_json(SAMPLE_INPUT, sample_result)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)  # якщо файл не валідний JSON — кине виняток
        assert data is not None

    # Тест нормальних умов 3
    def test_json_contains_required_keys(self, sample_result, tmp_path, monkeypatch):
        """JSON файл має містити всі обов'язкові секції."""
        import json
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = export_json(SAMPLE_INPUT, sample_result)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Перевіряємо наявність всіх ключових секцій
        assert "metadata" in data
        assert "project_parameters" in data
        assert "assessment_result" in data
        assert "feature_importance" in data

    # Тест нормальних умов 4
    def test_json_contains_risk_label(self, sample_result, tmp_path, monkeypatch):
        """JSON має містити правильну мітку ризику."""
        import json
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = export_json(SAMPLE_INPUT, sample_result)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["assessment_result"]["risk_label"] == sample_result["risk_label"]

    # Тест граничних умов 1
    def test_json_has_correct_extension(self, sample_result, tmp_path, monkeypatch):
        """Файл має мати розширення .json."""
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = export_json(SAMPLE_INPUT, sample_result)
        assert filepath.endswith(".json")

    # Тест граничних умов 2
    def test_json_unique_filenames(self, sample_result, tmp_path, monkeypatch):
        """Два JSON звіти підряд мають мати різні імена."""
        import time
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        path1 = export_json(SAMPLE_INPUT, sample_result)
        time.sleep(1)
        path2 = export_json(SAMPLE_INPUT, sample_result)
        assert path1 != path2

    # Тест виняткових ситуацій 1
    def test_json_with_empty_input(self, sample_result, tmp_path, monkeypatch):
        """export_json() з порожніми input_data → не падає."""
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        try:
            filepath = export_json({}, sample_result)
            assert os.path.exists(filepath)
        except Exception as e:
            pytest.fail(f"export_json() кинув виняток з порожніми даними: {e}")

    # Тест виняткових ситуацій 2 — РЕГРЕСІЙНИЙ
    def test_excel_still_works_after_json_added(self, sample_result, tmp_path, monkeypatch):
        """
        РЕГРЕСІЙНИЙ ТЕСТ: перевіряємо що додавання JSON функції
        не зламало існуючий Excel експорт.
        """
        import openpyxl
        monkeypatch.setattr(
            "app.ml.report.get",
            lambda key, default=None: str(tmp_path) if key == "paths.reports_dir" else default
        )
        filepath = generate_report(SAMPLE_INPUT, sample_result)
        assert filepath.endswith(".xlsx")
        wb = openpyxl.load_workbook(filepath)
        assert wb is not None
        wb.close()