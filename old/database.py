import sqlite3
import json
import logging

DATABASE_NAME = "tiny_verse_bot.db"

# Настройка логирования для модуля базы данных
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def init_db():
    """Инициализирует базу данных, создавая таблицу user_states, если она не существует."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                attacker_data TEXT,
                defender_data TEXT
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()


def save_user_data(user_id: int, attacker_data: dict, defender_data: dict):
    """Сохраняет данные атакующего и защищающегося для конкретного пользователя в базе данных."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Преобразуем словари в строки JSON
        attacker_json = json.dumps(attacker_data)
        defender_json = json.dumps(defender_data)

        # Используем REPLACE INTO для вставки или обновления записи
        cursor.execute("""
            REPLACE INTO user_states (user_id, attacker_data, defender_data)
            VALUES (?, ?, ?)
        """, (user_id, attacker_json, defender_json))
        conn.commit()
        logger.debug(f"Data saved for user {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Error saving data for user {user_id}: {e}")
    finally:
        if conn:
            conn.close()


def load_user_data(user_id: int):
    """Загружает данные атакующего и защищающегося для конкретного пользователя из базы данных."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT attacker_data, defender_data FROM user_states WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            attacker_json, defender_json = result
            # Преобразуем строки JSON обратно в словари
            attacker_data = json.loads(attacker_json)
            defender_data = json.loads(defender_json)
            logger.debug(f"Data loaded for user {user_id}")
            return attacker_data, defender_data
    except Exception as e:  # Catch broader exceptions for loading, especially JSON parsing errors
        logger.error(f"Error loading data for user {user_id}: {e}")
    finally:
        if conn:
            conn.close()

    logger.debug(f"No data found for user {user_id}")
    return None, None  # Возвращаем None,None если данных нет или произошла ошибка
