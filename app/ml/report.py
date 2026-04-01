# app/ml/report.py
# Генерація Excel звіту з результатами оцінки ризику проєкту

import os
from datetime import datetime

import openpyxl 
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)

from app.core.config import get
from app.core.logger import logger
from app.ml.features import FEATURES, RISK_COLORS


def _get_risk_fill(risk_level: int) -> PatternFill:
    """Повертає заливку клітинки відповідно до рівня ризику."""
    # Прибираємо # з кольору і конвертуємо для openpyxl
    color_map = {
        0: "2ecc71",  # зелений
        1: "f39c12",  # помаранчевий
        2: "e74c3c"   # червоний
    }
    color = color_map.get(risk_level, "ffffff")
    return PatternFill(start_color=color, end_color=color, fill_type="solid")


def _thin_border() -> Border:
    """Повертає тонку рамку для клітинок таблиці."""
    thin = Side(style="thin")
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def generate_report(input_data: dict, result: dict) -> str:
    """
    Генерує Excel звіт з результатами оцінки ризику.

    input_data — словник введених параметрів проєкту
    result     — словник результатів від predict()

    Повертає шлях до збереженого файлу.
    """
    # Створюємо папку для звітів якщо не існує
    reports_dir = get("paths.reports_dir", "data/reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Ім'я файлу містить дату і час — кожен звіт унікальний
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"risk_report_{timestamp}.xlsx"
    filepath = os.path.join(reports_dir, filename)

    # Створюємо новий Excel файл
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Оцінка ризику"

    # --- Стилі ---
    header_font = Font(bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="2c3e50", end_color="2c3e50", fill_type="solid")
    title_font = Font(bold=True, size=14)
    center = Alignment(horizontal="center", vertical="center")
    border = _thin_border()

    # --- Заголовок звіту ---
    ws.merge_cells("A1:C1")
    ws["A1"] = f"Звіт оцінки ризику проєкту"
    ws["A1"].font = Font(bold=True, size=16)
    ws["A1"].alignment = center

    ws.merge_cells("A2:C2")
    app_name = get("app.name", "Project Risk AI")
    version = get("app.version", "1.0.0")
    ws["A2"] = f"{app_name} v{version} | {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    ws["A2"].alignment = center
    ws["A2"].font = Font(italic=True, color="7f8c8d")

    ws.append([])  # порожній рядок

    # --- Блок: Результат оцінки ---
    ws.append(["РЕЗУЛЬТАТ ОЦІНКИ"])
    ws[f"A{ws.max_row}"].font = Font(bold=True, size=12)

    # Рівень ризику з кольоровою заливкою
    risk_row = ws.max_row + 1
    ws.cell(risk_row, 1, "Рівень ризику:")
    ws.cell(risk_row, 1).font = Font(bold=True)

    ws.cell(risk_row, 2, result["risk_label"])
    ws.cell(risk_row, 2).font = Font(bold=True, size=12)
    ws.cell(risk_row, 2).fill = _get_risk_fill(result["risk_level"])
    ws.cell(risk_row, 2).alignment = center
    ws.cell(risk_row, 2).border = border

    ws.append([])  # порожній рядок

    # --- Блок: Ймовірності ---
    ws.append(["Ймовірності по рівнях ризику"])
    ws[f"A{ws.max_row}"].font = Font(bold=True)

    # Заголовки таблиці ймовірностей
    prob_header_row = ws.max_row + 1
    headers = ["Рівень ризику", "Ймовірність", ""]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(prob_header_row, col, header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # Дані ймовірностей
    for label, prob in result["probabilities"].items():
        row = ws.max_row + 1
        ws.cell(row, 1, label).border = border
        ws.cell(row, 2, f"{prob * 100:.1f}%").border = border
        ws.cell(row, 2).alignment = center

    ws.append([])  # порожній рядок

    # --- Блок: Введені параметри ---
    ws.append(["Введені параметри проєкту"])
    ws[f"A{ws.max_row}"].font = Font(bold=True)

    # Заголовки таблиці параметрів
    param_header_row = ws.max_row + 1
    for col, header in enumerate(["Параметр", "Значення", ""], 1):
        cell = ws.cell(param_header_row, col, header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # Дані параметрів — беремо label з FEATURES для зрозумілих назв
    for feature in FEATURES:
        key = feature["key"]
        label = feature["label"]
        value = input_data.get(key, "—")

        row = ws.max_row + 1
        ws.cell(row, 1, label).border = border
        ws.cell(row, 2, value).border = border
        ws.cell(row, 2).alignment = center

    ws.append([])  # порожній рядок

    # --- Блок: Важливість факторів ---
    ws.append(["Важливість факторів (вплив на ризик)"])
    ws[f"A{ws.max_row}"].font = Font(bold=True)

    imp_header_row = ws.max_row + 1
    for col, header in enumerate(["Фактор", "Важливість", ""], 1):
        cell = ws.cell(imp_header_row, col, header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center
        cell.border = border

    # feature_importance вже відсортований за спаданням у model.py
    feature_labels = {f["key"]: f["label"] for f in FEATURES}
    for key, importance in result["feature_importance"].items():
        row = ws.max_row + 1
        ws.cell(row, 1, feature_labels.get(key, key)).border = border
        ws.cell(row, 2, f"{importance * 100:.2f}%").border = border
        ws.cell(row, 2).alignment = center

    # Ширина колонок
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 10

    # Зберігаємо файл
    wb.save(filepath)
    logger.info(f"Звіт збережено: {filepath}")

    return filepath