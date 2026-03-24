# app/gui/input_form.py
# Форма введення параметрів проєкту з валідацією

import customtkinter as ctk
import tkinter.messagebox as mb

from app.core.logger import logger
from app.ml.features import FEATURES, validate_input
from app.ml.model import load_model, predict


class InputForm(ctk.CTkToplevel):
    """
    Вікно форми введення параметрів проєкту.
    CTkToplevel — дочірнє вікно поверх головного.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Нова оцінка ризику")
        self.geometry("560x700")
        self.resizable(False, True)
        self._center_window(560, 700)

        # Робимо вікно модальним — блокує головне вікно
        self.grab_set()
        self.focus_set()

        # Завантажуємо модель при відкритті форми
        self.model = load_model()

        # Словник для зберігання полів вводу {key: CTkEntry}
        self.entries = {}

        # Словник для зберігання міток помилок {key: CTkLabel}
        self.error_labels = {}

        logger.info("Форму введення відкрито")
        self._build_ui()

    def _center_window(self, width: int, height: int):
        """Центрує вікно на екрані."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Будує інтерфейс форми."""

        # Заголовок
        ctk.CTkLabel(
            self,
            text="Параметри проєкту",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self,
            text="Заповніть всі поля для отримання оцінки ризику",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 15))

        # Прокручуваний фрейм для полів форми
        # ScrollableFrame дозволяє прокручувати якщо полів забагато
        scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=480)
        scroll_frame.pack(padx=20, pady=(0, 10), fill="both", expand=True)

        # Генеруємо поля для кожного параметра з FEATURES
        for feature in FEATURES:
            self._create_field(scroll_frame, feature)

        # Кнопки внизу форми
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🔍  Оцінити ризик",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=45,
            command=self._submit
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="↺  Очистити",
            font=ctk.CTkFont(size=13),
            width=130,
            height=45,
            fg_color="gray",
            hover_color="#555555",
            command=self._clear_form
        ).pack(side="left", padx=10)

    def _create_field(self, parent, feature: dict):
        """
        Створює одне поле форми для параметра.
        Кожне поле складається з:
        - Label з назвою параметра
        - Entry для введення значення
        - Label для відображення помилки валідації
        """
        key = feature["key"]

        # Контейнер для одного поля
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", pady=6)

        # Назва параметра
        ctk.CTkLabel(
            field_frame,
            text=feature["label"],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x")

        # Підказка під назвою
        ctk.CTkLabel(
            field_frame,
            text=feature["hint"],
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        ).pack(fill="x")

        # Поле введення з дефолтним значенням
        entry = ctk.CTkEntry(
            field_frame,
            placeholder_text=str(feature["default"]),
            width=460,
            height=36
        )
        entry.insert(0, str(feature["default"]))  # вставляємо дефолтне значення
        entry.pack(fill="x", pady=(3, 0))

        # Мітка для помилки (спочатку порожня)
        error_label = ctk.CTkLabel(
            field_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#e74c3c",  # червоний колір для помилок
            anchor="w"
        )
        error_label.pack(fill="x")

        # Зберігаємо посилання на поля для подальшого доступу
        self.entries[key] = entry
        self.error_labels[key] = error_label

    def _validate_all(self) -> tuple[bool, dict]:
        """
        Валідує всі поля форми.

        Повертає (all_valid, converted_values):
        - all_valid: True якщо всі поля валідні
        - converted_values: словник з конвертованими значеннями
        """
        all_valid = True
        values = {}

        for feature in FEATURES:
            key = feature["key"]
            raw_value = self.entries[key].get()  # отримуємо текст з поля

            is_valid, error_msg, converted = validate_input(key, raw_value)

            if is_valid:
                # Очищаємо помилку якщо поле валідне
                self.error_labels[key].configure(text="")
                values[key] = converted
            else:
                # Показуємо помилку під полем
                self.error_labels[key].configure(text=f"⚠ {error_msg}")
                all_valid = False

        return all_valid, values

    def _submit(self):
        """Обробляє натискання кнопки 'Оцінити ризик'."""
        logger.info("Спроба відправки форми")

        # Валідуємо всі поля
        all_valid, values = self._validate_all()

        if not all_valid:
            # Показуємо загальне повідомлення про помилки
            mb.showwarning(
                "Помилка валідації",
                "Будь ласка, виправте помилки у виділених полях."
            )
            logger.warning("Форма не пройшла валідацію")
            return

        # Всі поля валідні — робимо передбачення
        logger.info(f"Параметри форми: {values}")

        result = predict(self.model, values)
        logger.info(f"Результат оцінки: {result['risk_label']}")

        # Закриваємо форму і відкриваємо вікно результатів
        self.destroy()

        from app.gui.result_view import ResultView
        ResultView(self.master, values, result)

    def _clear_form(self):
        """Очищає всі поля і повертає дефолтні значення."""
        for feature in FEATURES:
            key = feature["key"]
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, str(feature["default"]))
            self.error_labels[key].configure(text="")

        logger.info("Форму очищено")