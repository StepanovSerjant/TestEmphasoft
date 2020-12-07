# Тестовое задание для Emphasoft.

## Ендпоинты:
- Создание нового пользователя (Регистрация) (POST -- <localhost>/users/register)
- Логин (получение токена для запросов) (POST -- <localhost>/users/login)

Для того, чтобы иметь доступ к следующим ендпоинтам нужно быть супер-пользователем. Для безопасности статус супер-пользователя присвается непосредстенно в базе.
- Получение списка пользователей (GET -- <localhost>/users)
- Получение пользователя по id (GET -- <localhost>/users/{id})
- Удаление пользователя (DELETE -- <localhost>/users{id})
- Частиное изменение данных пользователя (PATCH -- <localhost>/users/{id})
- Изменение данных пользователя (PUT -- <localhost>/users/{id})

## Установка:

### Клонирование репозитория
```
    mkdir TestEmphasoft
    cd TestEmphasoft
    git clone https://github.com/StepanovSerjant/TestEmphasoft.git
```

### Создание и активирование виртуального окружения
___Windows___
```
    python -m venv .venv
    .venv\Scripts\activate
```
___Linux___
```
    /usr/bin/python3 -m venv .venv
    source .venv/bin/activate
```

### Установка необходимых пакетов из файла зависимостей
```
    pip install -r requirements.txt
```

### Настройка данных конфигурации

Прошу обратить ваше внимание, что необходимо указать настройки для базы данных в файле _.env_

### Миграции

```
    alembic revision --autogenerate -m "Message"
    alembic upgrade head
```

### Запуск
```
    uvicorn main:app --reload
```
