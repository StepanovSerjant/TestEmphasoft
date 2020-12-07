from datetime import datetime, timedelta

from sqlalchemy import and_, select
from asyncpg.exceptions import UniqueViolationError
from fastapi.encoders import jsonable_encoder

from core.db import database
from users.models import tokens_table, users_table
from users.schemas import UserCreate, UserUpdate, UserPartialUpdate
from users.utils import get_random_string, hash_password, validate_password


async def get_user(user_id: int):
    query = users_table.select().where(users_table.c.id == user_id)
    return await database.fetch_one(query)


async def get_token_info(id: int):
    """ Получение данных о токене по айди пользователя """
    query = tokens_table.select().where(tokens_table.c.user == id)
    token_data = await database.fetch_one(query)
    token_info = {
        "token": token_data["token"],
        "expires": token_data["expires"]
    }
    return token_info


async def get_user_by_email(email: str):
    query = users_table.select().where(users_table.c.email == email)
    return await database.fetch_one(query)


async def create_user(user: UserCreate):
    """ Создание пользователя в БД """
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    query = users_table.insert().values(
        email=user.email,
        first_name=user.first_name, 
        last_name=user.last_name,
        hashed_password=f"{salt}${hashed_password}"
    )
    user_id = await database.execute(query)
    await create_user_token(user_id)

    return {**user.dict(), "id": user_id, "is_active": True}


async def create_user_token(user_id: int):
    """ Создание токена """
    query = (
        tokens_table.insert()
        .values(expires=datetime.now() + timedelta(weeks=2), user=user_id)
        .returning(tokens_table.c.token, tokens_table.c.expires)
    )

    return await database.fetch_one(query)


async def get_user_by_token(token: str):
    query = tokens_table.join(users_table).select().where(
        and_(
            tokens_table.c.token == token,
            tokens_table.c.expires > datetime.now()
        )
    )
    return await database.fetch_one(query)


async def delete_user(id: int):
    """ Удаление пользователя из БД + """
    user = await get_user(id)
    if user:
        query = users_table.delete().where(users_table.c.id == id)
        await database.fetch_one(query)
        return True
    return False


async def update_user(id: int, user_data: UserCreate):
    stored_user = await get_user(id)
    if not stored_user:
        return {"is_updated": None, "msg": "User not found"}

    user_data_encoded = jsonable_encoder(user_data)
    user_data_encoded["id"] = id
    user_data_encoded["hashed_password"] = stored_user["hashed_password"]
    if not validate_password(
            user_data_encoded["password"], stored_user["hashed_password"]
        ):
        salt = get_random_string()
        new_password = f"{salt}${hash_password(user_data.password, salt)}"
        user_data_encoded["hashed_password"] = new_password
    
    try:
        del user_data_encoded["password"]
        query = users_table.update().where(users_table.c.id == id).values(**user_data_encoded)
        await database.execute(query)
    except UniqueViolationError:
        return {"is_updated": None, "msg": "Email already registered"}
    
    return {
        "is_updated": jsonable_encoder(user_data)
    }


async def partial_update_user(id: int, user_data: UserPartialUpdate):
    stored_user = await get_user(id)
    if not stored_user:
        return None

    update_data = user_data.dict(exclude_unset=True)
    if "hashed_password" in update_data:
        stored_user = dict(stored_user)
        if not validate_password(
                user_data.hashed_password, stored_user["hashed_password"]
            ):
            salt = get_random_string()
            new_password = f"{salt}${hash_password(user_data.hashed_password, salt)}"
            update_data["hashed_password"] = new_password
        else:
            update_data["hashed_password"] = stored_user["hashed_password"]
        
    updated_item = UserPartialUpdate(**stored_user).copy(update=update_data)
    query = users_table.update().where(users_table.c.id == id).values(**updated_item.dict())
    await database.execute(query)
    
    updated_item.hashed_password = user_data.hashed_password
    return updated_item


async def get_user_list():
    user_list = await database.fetch_all(query=users_table.select())
    user_list = [dict(user) for user in user_list]
    return user_list

