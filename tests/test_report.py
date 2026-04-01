# tests/test_report.py
# Тести для модуля генерації звітів (app/ml/report.py)

import pytest
import os
import openpyxl
from unittest.mock import patch
from app.ml.report import generate_report
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