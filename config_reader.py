from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: SecretStr
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra="ignore"
    )


secrets = Settings()

bot = Bot(
    token=secrets.token.get_secret_value(),
    default=DefaultBotProperties(parse_mode="HTML"),
)
