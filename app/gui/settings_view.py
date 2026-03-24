# app/gui/settings_view.py
# Вікно налаштувань програми

import customtkinter as ctk
import tkinter.messagebox as mb

from app.core.config import load_config, save_config, get
from app.core.logger import logger


class SettingsView(ctk.CTkToplevel):
    """Вікно налаштувань — дозволяє змінювати тему та параметри моделі."""

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.title("Налаштування")
        self.geometry("450x600")
        self.resizable(False, False)
        self._center_window(450, 500)

        self.grab_set()
        self.focus_set()

        # Завантажуємо поточний конфіг
        self.config = load_config()

        logger.info("Вікно налаштувань відкрито")
        self._build_ui()

    def _center_window(self, width: int, height: int):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Будує інтерфейс вікна налаштувань."""

        ctk.CTkLabel(
            self,
            text="Налаштування",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 15))

        # --- Секція: Зовнішній вигляд ---
        self._section_label("🎨  Зовнішній вигляд")

        # Вибір теми
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(
            theme_frame,
            text="Тема інтерфейсу:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self.theme_var = ctk.StringVar(
            value=self.config.get("appearance", {}).get("theme", "dark")
        )

        ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            variable=self.theme_var,
            width=140
        ).pack(side="right")

        # Вибір кольорової схеми
        color_frame = ctk.CTkFrame(self, fg_color="transparent")
        color_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(
            color_frame,
            text="Кольорова схема:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self.color_var = ctk.StringVar(
            value=self.config.get("appearance", {}).get("color_scheme", "blue")
        )

        ctk.CTkOptionMenu(
            color_frame,
            values=["blue", "green", "dark-blue"],
            variable=self.color_var,
            width=140
        ).pack(side="right")

        # --- Секція: Параметри моделі ---
        self._section_label("🤖  Параметри моделі")

        # Кількість дерев
        trees_frame = ctk.CTkFrame(self, fg_color="transparent")
        trees_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(
            trees_frame,
            text="Кількість дерев (50–500):",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self.trees_entry = ctk.CTkEntry(trees_frame, width=80)
        self.trees_entry.insert(
            0, str(self.config.get("model", {}).get("n_estimators", 100))
        )
        self.trees_entry.pack(side="right")

        # Розмір тестової вибірки
        test_frame = ctk.CTkFrame(self, fg_color="transparent")
        test_frame.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(
            test_frame,
            text="Розмір тесту (0.1–0.4):",
            font=ctk.CTkFont(size=13)
        ).pack(side="left")

        self.test_entry = ctk.CTkEntry(test_frame, width=80)
        self.test_entry.insert(
            0, str(self.config.get("model", {}).get("test_size", 0.2))
        )
        self.test_entry.pack(side="right")

        # --- Версія програми (тільки читання) ---
        self._section_label("ℹ️  Інформація")

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=30, pady=5)

        version = get("app.version", "1.0.0")
        ctk.CTkLabel(
            info_frame,
            text=f"Версія програми: {version}",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(side="left")

        # --- Кнопки ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="💾  Зберегти",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=150,
            height=40,
            command=self._save
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="✖  Скасувати",
            font=ctk.CTkFont(size=13),
            width=130,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self.destroy
        ).pack(side="left", padx=10)

    def _section_label(self, text: str):
        """Створює заголовок секції з роздільником."""
        ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=30, pady=(15, 2))

        ctk.CTkFrame(self, height=1, fg_color="gray").pack(
            fill="x", padx=30, pady=(0, 5)
        )

    def _save(self):
        """Валідує і зберігає налаштування в config.json."""

        # Валідація кількості дерев
        try:
            n_estimators = int(self.trees_entry.get())
            if not (50 <= n_estimators <= 500):
                raise ValueError
        except ValueError:
            mb.showwarning(
                "Помилка",
                "Кількість дерев має бути цілим числом від 50 до 500"
            )
            return

        # Валідація розміру тестової вибірки
        try:
            test_size = float(self.test_entry.get().replace(",", "."))
            if not (0.1 <= test_size <= 0.4):
                raise ValueError
        except ValueError:
            mb.showwarning(
                "Помилка",
                "Розмір тесту має бути числом від 0.1 до 0.4"
            )
            return

        # Зберігаємо в конфіг
        self.config["appearance"]["theme"] = self.theme_var.get()
        self.config["appearance"]["color_scheme"] = self.color_var.get()
        self.config["model"]["n_estimators"] = n_estimators
        self.config["model"]["test_size"] = test_size

        save_config(self.config)
        logger.info(f"Налаштування збережено: тема={self.theme_var.get()}")

        # Застосовуємо тему одразу
        ctk.set_appearance_mode(self.theme_var.get())
        ctk.set_default_color_theme(self.color_var.get())

        mb.showinfo("Збережено", "Налаштування збережено успішно!")
        self.destroy()