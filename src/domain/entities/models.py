from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.entities.enums import (
    CodeStatus,
    TransactionType,
)


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

    balance_ref: Mapped[UserBalance] = relationship(back_populates="user_ref", lazy="raise")
    role_ref: Mapped["Role"] = relationship("Role", lazy="raise")


class UserBalance(Base):
    __tablename__ = "user_balances"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), server_default="0.00", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    user_ref: Mapped[User] = relationship(back_populates="balance_ref", lazy="raise")


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        PgEnum(
            TransactionType,
            name="transaction_type_enum",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    new_balance: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    code_redemption_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("code_redemptions.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user_ref: Mapped[User] = relationship(back_populates="balance_ref", lazy="raise")
    redemption_ref: Mapped[CodeRedemptions | None] = relationship(lazy="raise")


class Role(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Code(Base):
    __tablename__ = "codes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    status: Mapped[CodeStatus] = mapped_column(
        PgEnum(
            CodeStatus,
            name="code_status_enum",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        server_default=CodeStatus.ACTIVE,
        nullable=False,
    )
    max_uses: Mapped[int] = mapped_column(server_default="1", nullable=False)
    uses_count: Mapped[int] = mapped_column(server_default="0", nullable=False)
    max_uses_per_user: Mapped[int] = mapped_column(server_default="1", nullable=False)
    starts_at: Mapped[datetime | None] = mapped_column(nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(),nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    created_by_ref: Mapped["User"] = relationship("User", lazy="raise")
    updated_by_ref: Mapped["User"] = relationship("User", lazy="raise")

    redemptions: Mapped[list["CodeRedemptions"]] = relationship(
        "CodeRedemptions",
        back_populates="code_ref",
        lazy="raise"
    )


class CodeRedemptions(Base):
    __tablename__ = "code_redemptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("codes.id", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user_ref: Mapped["User"] = relationship("User", lazy="raise")
    code_ref: Mapped["Code"] = relationship("Code", back_populates="redemptions", lazy="raise")
