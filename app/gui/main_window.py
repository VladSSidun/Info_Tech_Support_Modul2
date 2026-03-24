# app/gui/main_window.py
# Головне вікно програми

import customtkinter as ctk
from app.core.config import get
from app.core.logger import logger


class MainWindow(ctk.CTk):
    """
    Головне вікно програми.
    Наслідує CTk — це базовий клас вікна у customtkinter.
    """

    def __init__(self):
        super().__init__()

        # Застосовуємо тему з конфігу
        theme = get("appearance.theme", "dark")
        color = get("appearance.color_scheme", "blue")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme(color)

        # Налаштування вікна
        app_name = get("app.name", "Project Risk AI")
        version = get("app.version", "1.0.0")
        self.title(f"{app_name} v{version}")
        self.geometry("500x400")
        self.resizable(False, False)

        # Центруємо вікно на екрані
        self._center_window(500, 400)

        logger.info("Головне вікно ініціалізовано")
        self._build_ui()

    def _center_window(self, width: int, height: int):
        """Розміщує вікно по центру екрану."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Будує всі елементи інтерфейсу головного вікна."""

        # --- Заголовок ---
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(40, 10))

        ctk.CTkLabel(
            title_frame,
            text="🛡️ Project Risk AI",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack()

        ctk.CTkLabel(
            title_frame,
            text="Інтелектуальна система оцінювання ризику проєкту",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(pady=(5, 0))

        version = get("app.version", "1.0.0")
        ctk.CTkLabel(
            title_frame,
            text=f"Версія {version}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack()

        # --- Кнопки навігації ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)

        # Кнопка нової оцінки — головна дія
        ctk.CTkButton(
            btn_frame,
            text="🔍  Нова оцінка ризику",
            font=ctk.CTkFont(size=15, weight="bold"),
            width=280,
            height=50,
            command=self._open_input_form
        ).pack(pady=8)

        # Кнопка налаштувань
        ctk.CTkButton(
            btn_frame,
            text="⚙️  Налаштування",
            font=ctk.CTkFont(size=13),
            width=280,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self._open_settings
        ).pack(pady=8)

        # Кнопка "Про програму"
        ctk.CTkButton(
            btn_frame,
            text="ℹ️  Про програму",
            font=ctk.CTkFont(size=13),
            width=280,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self._show_about
        ).pack(pady=8)

        # --- Футер ---
        ctk.CTkLabel(
            self,
            text="© 2026 Project Risk AI",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="bottom", pady=10)

    def _open_input_form(self):
        """Відкриває форму введення параметрів проєкту."""
        # Імпортуємо тут щоб уникнути циклічних імпортів
        from app.gui.input_form import InputForm
        logger.info("Відкрито форму введення параметрів")
        InputForm(self)

    def _open_settings(self):
        """Відкриває вікно налаштувань."""
        from app.gui.settings_view import SettingsView
        logger.info("Відкрито налаштування")
        SettingsView(self)

    def _show_about(self):
        """Показує діалог з інформацією про програму."""
        app_name = get("app.name", "Project Risk AI")
        version = get("app.version", "1.0.0")

        # CTkMessagebox — простий діалог через стандартний tkinter
        import tkinter.messagebox as mb
        mb.showinfo(
            "Про програму",
            f"{app_name}\n"
            f"Версія: {version}\n\n"
            f"Система оцінювання ризику зриву термінів\n"
            f"IT-проєктів на основі машинного навчання.\n\n"
            f"Алгоритм: Random Forest Classifier"
        )
        logger.info("Показано вікно 'Про програму'")