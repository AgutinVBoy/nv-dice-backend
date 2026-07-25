from pathlib import Path

from pydantic import SecretStr, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_project_meta() -> tuple[str, str]:
    try:
        import __meta__
        return __meta__.__version__, __meta__.__app_name__
    except ImportError:
        import tomllib

        pyproject_path = Path(__file__).parents[2] / "pyproject.toml"
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)["project"]
                return data["version"], data["name"]
        except (FileNotFoundError, KeyError):
            return "0.0.0-dev", "local-dev"


_SYSTEM_VERSION, _SYSTEM_NAME = _get_project_meta()


class Settings(BaseSettings):
    @property
    def app_version(self) -> str:
        return _SYSTEM_VERSION

    @property
    def app_name(self) -> str:
        return _SYSTEM_NAME

    APP_TITLE: str = "nv-dice"

    LOG_LEVEL: str = "INFO"
    LOCALE: str = "ru"

    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_DB_NAME: str

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def redis_url(self) -> str:
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            username=self.REDIS_USER,
            password=self.REDIS_PASSWORD,
            path=self.REDIS_DB_NAME
        ).unicode_string()


settings = Settings()
