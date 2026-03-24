# app/gui/result_view.py
# Вікно відображення результатів оцінки ризику з графіками

import customtkinter as ctk
import tkinter.messagebox as mb
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from app.core.logger import logger
from app.ml.features import FEATURES, RISK_COLORS
from app.ml.report import generate_report


class ResultView(ctk.CTkToplevel):
    """
    Вікно результатів оцінки ризику.
    Показує рівень ризику, графіки та кнопку збереження звіту.
    """

    def __init__(self, parent, input_data: dict, result: dict):
        super().__init__(parent)

        self.input_data = input_data
        self.result = result

        self.title("Результат оцінки ризику")
        self.geometry("700x750")
        self.resizable(False, True)
        self._center_window(700, 750)

        self.grab_set()
        self.focus_set()

        logger.info("Вікно результатів відкрито")
        self._build_ui()

    def _center_window(self, width: int, height: int):
        """Центрує вікно на екрані."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        """Будує інтерфейс вікна результатів."""

        risk_level = self.result["risk_level"]
        risk_label = self.result["risk_label"]
        color = RISK_COLORS[risk_level]

        # --- Заголовок з рівнем ризику ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(20, 5))

        ctk.CTkLabel(
            header_frame,
            text="Результат оцінки",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack()

        # Велика кольорова мітка рівня ризику
        risk_icons = {0: "🟢", 1: "🟡", 2: "🔴"}
        ctk.CTkLabel(
            header_frame,
            text=f"{risk_icons[risk_level]}  Рівень ризику: {risk_label}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color
        ).pack(pady=10)

        # Ймовірності у вигляді тексту
        probs = self.result["probabilities"]
        prob_text = "  |  ".join(
            [f"{label}: {prob*100:.1f}%" for label, prob in probs.items()]
        )
        ctk.CTkLabel(
            header_frame,
            text=prob_text,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        # --- Графіки ---
        self._build_charts()

        # --- Кнопки ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame,
            text="💾  Зберегти звіт (Excel)",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=220,
            height=42,
            command=self._save_report
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🔍  Нова оцінка",
            font=ctk.CTkFont(size=13),
            width=160,
            height=42,
            fg_color="gray",
            hover_color="#555555",
            command=self._new_assessment
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="✖  Закрити",
            font=ctk.CTkFont(size=13),
            width=120,
            height=42,
            fg_color="gray",
            hover_color="#555555",
            command=self.destroy
        ).pack(side="left", padx=10)

    def _build_charts(self):
        """Будує два графіки: pie chart і bar chart важливості факторів."""

        # Визначаємо чи темна тема активна
        is_dark = ctk.get_appearance_mode().lower() == "dark"
        bg_color = "#2b2b2b" if is_dark else "#f0f0f0"
        text_color = "white" if is_dark else "black"

        # Створюємо фігуру з двома підграфіками
        fig, (ax1, ax2) = plt.subplots(
            1, 2,
            figsize=(6.5, 3.2),
            facecolor=bg_color
        )

        # --- Графік 1: Pie chart ймовірностей ---
        probs = self.result["probabilities"]
        labels = list(probs.keys())
        sizes = list(probs.values())
        pie_colors = [
            RISK_COLORS[0],   # зелений для Низького
            RISK_COLORS[1],   # помаранчевий для Середнього
            RISK_COLORS[2]    # червоний для Високого
        ]

        # Виділяємо сектор з найвищим ризиком
        explode = [0.05] * len(sizes)

        wedges, texts, autotexts = ax1.pie(
            sizes,
            labels=labels,
            colors=pie_colors,
            explode=explode,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"color": text_color, "fontsize": 9}
        )

        for autotext in autotexts:
            autotext.set_color(text_color)

        ax1.set_title(
            "Розподіл ймовірностей",
            color=text_color,
            fontsize=11,
            pad=10
        )
        ax1.set_facecolor(bg_color)

        # --- Графік 2: Bar chart важливості факторів ---
        importance = self.result["feature_importance"]

        # Беремо топ-6 найважливіших факторів
        top_items = list(importance.items())[:6]
        factor_keys = [item[0] for item in top_items]
        factor_values = [item[1] * 100 for item in top_items]

        # Отримуємо короткі назви факторів для підписів
        feature_short_names = {f["key"]: f["label"].split("(")[0].strip()
                               for f in FEATURES}
        factor_labels = [feature_short_names.get(k, k) for k in factor_keys]

        # Скорочуємо довгі назви для читабельності
        factor_labels = [
            label[:20] + "..." if len(label) > 20 else label
            for label in factor_labels
        ]

        bar_colors = ["#3498db"] * len(factor_values)
        bars = ax2.barh(
            factor_labels,
            factor_values,
            color=bar_colors,
            edgecolor="none"
        )

        # Підписи значень на барах
        for bar, val in zip(bars, factor_values):
            ax2.text(
                bar.get_width() + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%",
                va="center",
                color=text_color,
                fontsize=8
            )

        ax2.set_title(
            "Вплив факторів (топ-6)",
            color=text_color,
            fontsize=11,
            pad=10
        )
        ax2.set_facecolor(bg_color)
        ax2.tick_params(colors=text_color, labelsize=8)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["bottom"].set_color("gray")
        ax2.spines["left"].set_color("gray")
        ax2.set_xlabel("Важливість (%)", color=text_color, fontsize=9)
        ax2.invert_yaxis()  # найважливіший фактор зверху

        plt.tight_layout(pad=1.5)

        # Вбудовуємо matplotlib графік у tkinter вікно
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=15, pady=5, fill="both")

        # Закриваємо figure щоб не витікала пам'ять
        plt.close(fig)

    def _save_report(self):
        """Зберігає Excel звіт і показує повідомлення про успіх."""
        try:
            filepath = generate_report(self.input_data, self.result)
            logger.info(f"Звіт збережено користувачем: {filepath}")
            mb.showinfo(
                "Звіт збережено",
                f"Звіт успішно збережено:\n{filepath}"
            )
        except Exception as e:
            logger.error(f"Помилка збереження звіту: {e}")
            mb.showerror(
                "Помилка",
                f"Не вдалося зберегти звіт:\n{str(e)}"
            )

    def _new_assessment(self):
        """Закриває поточне вікно і відкриває нову форму оцінки."""
        self.destroy()
        from app.gui.input_form import InputForm
        InputForm(self.master)
        logger.info("Розпочато нову оцінку")