from pydantic_settings import BaseSettings


class Key(BaseSettings):
    openai: str


class Bot(BaseSettings):
    token: str


class DB(BaseSettings):
    host: str
    port: int
    name: str
    user: str
    password: str


class Config(BaseSettings):
    bot: Bot
    db: DB
    key: Key

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(env_file=".env") -> Config:
    config = Config(_env_file=env_file)  # type: ignore
    return config
