from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(10), ForeignKey("roles.code", onupdate="CASCADE"))
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())
    password: Mapped[str] = mapped_column(Text, nullable=False)
    password_updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    role_ref: Mapped[list["Role"]] = relationship("Role", secondary="roles", lazy="raise")


class Role(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())