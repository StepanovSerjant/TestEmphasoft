from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, text, sql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.dialects.postgresql import UUID

from core.db import Base


class User(Base):
    """ Таблица для хранения информации о пользователях """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(45), unique=True, index=True)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(150), nullable=True)
    hashed_password = Column(String)
    last_login = Column(DateTime(timezone=True), server_default=sql.func.now())
    is_active = Column(
        Boolean,
        server_default=expression.true(),
        nullable=False
    )
    is_super = Column(
        Boolean,
        server_default=expression.false(),
        nullable=False
    )

users_table = User.__table__


class Token(Base):
    """ Таблица для хранения информации о токенах пользователей """

    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(
        UUID(as_uuid=False), 
        server_default=text("uuid_generate_v4()"),
        unique=True,
        nullable=False,
        index=True
    )
    expires = Column(DateTime)
    user = Column(ForeignKey("users.id", ondelete='CASCADE'))
    user_id = relationship("User")


tokens_table = Token.__table__


