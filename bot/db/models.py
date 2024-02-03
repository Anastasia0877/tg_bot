import uuid
from datetime import datetime

from aiogram.utils.link import create_tg_link
from sqlalchemy import BigInteger, DateTime, func, Boolean, Enum
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from bot.structrures.enums import VarsEnum, ContentTypes


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    pay_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pay_forever: Mapped[bool] = mapped_column(Boolean, default=False)
    completed: Mapped[list] = mapped_column(MutableList.as_mutable(ARRAY(BigInteger)), default=[], nullable=True)
    balance: Mapped[int] = mapped_column(BigInteger, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class Variable(Base):
    __tablename__ = 'variables'

    name: Mapped[VarsEnum] = mapped_column(Enum(VarsEnum), primary_key=True)
    str_value: Mapped[str | None] = mapped_column()
    int_value: Mapped[int | None] = mapped_column()
    file_id: Mapped[str | None] = mapped_column()
    content_type: Mapped[ContentTypes | None] = mapped_column(Enum(ContentTypes))


class Info(Base):
    __tablename__ = 'info'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str | None] = mapped_column()
    state: Mapped[str | None] = mapped_column()
    contacts: Mapped[str | None] = mapped_column()
    links_first: Mapped[str | None] = mapped_column()
    links_second: Mapped[str | None] = mapped_column()
    links_third: Mapped[str | None] = mapped_column()
    term: Mapped[str | None] = mapped_column()
    amount: Mapped[str | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column()
    updated_notif: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class Query(Base):
    __tablename__ = 'queries'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger)
    result: Mapped[list[int]] = mapped_column(MutableList.as_mutable(ARRAY(BigInteger)))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
