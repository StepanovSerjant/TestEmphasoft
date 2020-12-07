import os

import databases
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy_utils import create_database, drop_database

import settings
from core.db import database


@pytest.fixture(scope="module")
def temp_db():

    DB_NAME = "db-for-tests"
    TEST_SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:5432/{DB_NAME}"
    )
    create_database(TEST_SQLALCHEMY_DATABASE_URL) # Создаем БД
    alembic_cfg = Config(os.path.join("C:/Users/Алексей/Desktop/my_new_api/alembic.ini")) # Загружаем конфигурацию alembic 
    command.upgrade(alembic_cfg, "head") # выполняем миграции

    try:
        yield databases.Database(TEST_SQLALCHEMY_DATABASE_URL)
    finally:
        drop_database(TEST_SQLALCHEMY_DATABASE_URL) # удаляем БД