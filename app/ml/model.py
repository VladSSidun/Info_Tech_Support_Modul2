# app/ml/model.py
# ML модуль: генерація даних, навчання і передбачення ризику проєкту

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.core.config import get
from app.core.logger import logger
from app.ml.features import get_feature_keys, RISK_LABELS


def generate_training_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Генерує синтетичні тренувальні дані для моделі.

    В реальному проєкті тут були б реальні дані з БД або CSV.
    Ми генеруємо дані з логікою: більша команда + більший досвід +
    більший бюджет + чіткі вимоги = менший ризик.

    Повертає DataFrame з колонками-параметрами + колонка 'risk_level'.
    """
    np.random.seed(get("model.random_state", 42))
    n = n_samples

    # Генеруємо випадкові значення для кожного параметра
    data = {
        "team_size":             np.random.randint(1, 51, n),
        "team_experience":       np.round(np.random.uniform(0, 20, n), 1),
        "budget":                np.round(np.random.uniform(10, 10000, n), 1),
        "duration_weeks":        np.random.randint(1, 105, n),
        "requirements_count":    np.random.randint(1, 501, n),
        "requirements_clarity":  np.round(np.random.uniform(0, 1, n), 2),
        "stakeholders_count":    np.random.randint(1, 21, n),
        "has_risk_manager":      np.random.randint(0, 2, n),
    }

    df = pd.DataFrame(data)

    # Розраховуємо "ризик" на основі логіки предметної області
    # risk_score: більше = гірше
    risk_score = (
        (50 - df["team_size"]) * 0.3 +           # менша команда = більший ризик
        (20 - df["team_experience"]) * 0.5 +      # менший досвід = більший ризик
        (10000 - df["budget"]) / 500 +             # менший бюджет = більший ризик
        df["duration_weeks"] * 0.2 +               # довший проєкт = більший ризик
        df["requirements_count"] * 0.05 +          # більше вимог = більший ризик
        (1 - df["requirements_clarity"]) * 10 +    # нечіткі вимоги = більший ризик
        df["stakeholders_count"] * 0.3 +           # більше стейкхолдерів = більший ризик
        (1 - df["has_risk_manager"]) * 5           # немає ризик-менеджера = більший ризик
    )

    # Додаємо невеликий шум щоб дані не були ідеальними
    noise = np.random.normal(0, 2, n)
    risk_score += noise

    # Конвертуємо числовий score в категорії 0/1/2
    # за допомогою перцентилів — рівномірний розподіл класів
    p33 = np.percentile(risk_score, 33)
    p66 = np.percentile(risk_score, 66)

    df["risk_level"] = np.where(
        risk_score <= p33, 0,           # Низький ризик
        np.where(risk_score <= p66, 1, 2)  # Середній або Високий
    )

    logger.info(f"Згенеровано {n} тренувальних зразків")
    return df


def train_model(df: pd.DataFrame = None) -> tuple:
    """
    Навчає RandomForest модель на тренувальних даних.

    Якщо df не передано — генерує дані автоматично.
    Зберігає навчену модель у файл model.pkl.

    Повертає (model, accuracy, report) — модель, точність і звіт.
    """
    if df is None:
        df = generate_training_data()

    feature_keys = get_feature_keys()
    X = df[feature_keys]   # вхідні параметри
    y = df["risk_level"]   # цільова змінна (0/1/2)

    # Розділяємо на тренувальну і тестову вибірки
    test_size = get("model.test_size", 0.2)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=get("model.random_state", 42)
    )

    # Навчаємо Random Forest
    n_estimators = get("model.n_estimators", 100)
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=get("model.random_state", 42)
    )
    model.fit(X_train, y_train)

    # Оцінюємо точність
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=[RISK_LABELS[i] for i in range(3)]
    )

    logger.info(f"Модель навчена. Точність: {accuracy:.2%}")

    # Зберігаємо модель у файл
    model_path = get("paths.model_file", "data/model.pkl")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    logger.info(f"Модель збережена: {model_path}")

    return model, accuracy, report


def load_model():
    """
    Завантажує збережену модель з файлу.
    Якщо файл не існує — навчає нову модель автоматично.
    """
    model_path = get("paths.model_file", "data/model.pkl")

    if os.path.exists(model_path):
        model = joblib.load(model_path)
        logger.info(f"Модель завантажена з файлу: {model_path}")
        return model
    else:
        # Модель ще не існує — навчаємо першу
        logger.warning("Файл моделі не знайдено. Навчаємо нову модель...")
        model, _, _ = train_model()
        return model


def predict(model, input_data: dict) -> dict:
    """
    Робить передбачення ризику для введених параметрів проєкту.

    input_data — словник з ключами як у FEATURES:
        {"team_size": 5, "team_experience": 2.0, ...}

    Повертає словник з результатами:
        {
            "risk_level": 1,
            "risk_label": "Середній",
            "probabilities": {"Низький": 0.2, "Середній": 0.6, "Високий": 0.2},
            "feature_importance": {"team_size": 0.15, ...}
        }
    """
    feature_keys = get_feature_keys()

    # Формуємо DataFrame з одного рядка для передбачення
    X = pd.DataFrame([{key: input_data[key] for key in feature_keys}])

    # Передбачення класу і ймовірностей
    risk_level = int(model.predict(X)[0])
    probabilities = model.predict_proba(X)[0]

    # Важливість кожного параметра для цього передбачення
    importance = dict(zip(feature_keys, model.feature_importances_))

    result = {
        "risk_level": risk_level,
        "risk_label": RISK_LABELS[risk_level],
        "probabilities": {
            RISK_LABELS[i]: round(float(probabilities[i]), 3)
            for i in range(len(probabilities))
        },
        "feature_importance": {
            k: round(v, 4) for k, v in
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        }
    }

    logger.info(f"Передбачення: {result['risk_label']} (рівень {risk_level})")
    return result