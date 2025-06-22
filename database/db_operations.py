import aiosqlite
import json
import logging

DATABASE_NAME = "tiny_verse_bot.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def init_db():
    """Инициализирует базу данных."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                attacker_data TEXT,
                defender_data TEXT
            )
        """)
        await db.commit()
        logger.info("Database initialized successfully.")


async def save_user_data(user_id: int, attacker_data: dict, defender_data: dict):
    """Сохраняет данные пользователя в базу данных."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        await db.execute("""
            REPLACE INTO user_states (user_id, attacker_data, defender_data)
            VALUES (?, ?, ?)
        """, (user_id, json.dumps(attacker_data), json.dumps(defender_data)))
        await db.commit()
        logger.info(f"User data for {user_id} saved successfully.")


async def load_user_data(user_id: int):
    """Загружает данные пользователя из базы данных."""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        async with db.execute("""
            SELECT attacker_data, defender_data FROM user_states WHERE user_id = ?
        """, (user_id,)) as cursor:
            result = await cursor.fetchone()

        if result:
            attacker_data = json.loads(result[0])
            defender_data = json.loads(result[1])
            logger.info(f"User data for {user_id} loaded successfully.")
            return attacker_data, defender_data

    logger.info(f"No data found for user {user_id}.")
    return None, None
