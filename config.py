import os

class DatabaseConfig:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
    DB_NAME = os.getenv("DB_NAME", "testdb")
    DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", 5))
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

class DockerConfig:
    MYSQL_CONTAINER_NAME = "mysql_container"

CONFIG = {
    "db": DatabaseConfig,
    "docker": DockerConfig
}