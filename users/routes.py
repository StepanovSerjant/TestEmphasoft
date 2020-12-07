from typing import List

from starlette import status
from starlette.responses import Response
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from users import dependencies, services, schemas, utils, models
from core.db import database

users_router = APIRouter()


@users_router.post(
    "/register", 
    status_code=201,
    response_model=schemas.UserBase
)
async def user_register(user: schemas.UserCreate):
    """ Создание нового пользователя """
    db_user = await services.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await services.create_user(user=user)


@users_router.post("/login", response_model=schemas.TokenBase)
async def user_auth(user_data: OAuth2PasswordRequestForm = Depends()):
    """ Процесс авторизации пользователя """
    user = await services.get_user_by_email(email=user_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not utils.validate_password(
        password=user_data.password, hashed_password=user["hashed_password"]
    ):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return await services.get_token_info(user["id"])


@users_router.get("/{id}", response_model=schemas.User)
async def user_read(
        id: int,
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    """ Получение данных конкретного пользователя """
    user = await services.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = await services.get_token_info(id)
    return {**current_user, "id": id, "is_active": True, "token": token_data}


@users_router.get("/", response_model=List[schemas.UserBase])
async def user_list(
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    """ Получение данных по всем пользователям """
    return await services.get_user_list()


@users_router.put("/{id}", response_model=schemas.UserUpdate)
async def user_update(
        id: int,
        user_data: schemas.UserUpdate,
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    """ Обновление данных пользователя """
    is_updated = await services.update_user(id, user_data)
    if not is_updated["is_updated"]:
        raise HTTPException(status_code=404, detail=is_updated["msg"])
    return is_updated["is_updated"]


@users_router.patch("/{id}")
async def user_partial_update(
        id: int,
        user_data: schemas.UserPartialUpdate,
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    """ Частичное обновление данных пользователя """
    updated_data = await services.partial_update_user(id, user_data)
    if not updated_data:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_data


@users_router.delete("/{id}", response_model=schemas.UserBase)
async def user_delete(
        id: int,
        current_user: schemas.User = Depends(dependencies.get_current_user)
    ):
    """ Удаление пользователя по айди + """
    is_deleted = await services.delete_user(id)
    if is_deleted:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="User not found")
