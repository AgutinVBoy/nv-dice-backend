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
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.entities.enums import (
    CodeStatus,
    TransactionType,
    GameResult,
    GameBetType,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("roles.code", onupdate="CASCADE"),
        server_default="'user'"
    )
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())
    password: Mapped[str] = mapped_column(Text, nullable=False)
    password_updated_at: Mapped[datetime] = mapped_column(server_default=func.now())

    balance_ref: Mapped[UserBalance] = relationship(back_populates="user_ref", lazy="raise")
    role_ref: Mapped[Role] = relationship(foreign_keys=[role], lazy="raise")


class UserBalance(Base):
    __tablename__ = "user_balances"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), server_default="0.00", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    user_ref: Mapped[User] = relationship(back_populates="balance_ref", foreign_keys=[user_id], lazy="raise")


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
    game_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("games.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user_ref: Mapped[User] = relationship(foreign_keys=[user_id], lazy="raise")
    redemption_ref: Mapped[CodeRedemptions | None] = relationship(foreign_keys=[code_redemption_id], lazy="raise")
    game_ref: Mapped[Game | None] = relationship(foreign_keys=[game_id], lazy="raise")


class Role(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Code(Base):
    __tablename__ = "codes"
    __mapper_args__ = {"eager_defaults": True}

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
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by_ref: Mapped[User] = relationship(foreign_keys=[created_by_id], lazy="raise")
    updated_by_ref: Mapped[User] = relationship(foreign_keys=[updated_by_id], lazy="raise")

    redemptions: Mapped[list[CodeRedemptions]] = relationship(back_populates="code_ref", lazy="raise")


class CodeRedemptions(Base):
    __tablename__ = "code_redemptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("codes.id"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user_ref: Mapped[User] = relationship(foreign_keys=[user_id], lazy="raise")
    code_ref: Mapped[Code] = relationship(back_populates="redemptions", foreign_keys=[code_id], lazy="raise")


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    result: Mapped[GameResult] = mapped_column(
        PgEnum(
            GameResult,
            name="game_result_enum",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
    )
    bet_amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    win_amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    probability: Mapped[int] = mapped_column(nullable=False)
    bet_type: Mapped[GameBetType] = mapped_column(
        PgEnum(
            GameBetType,
            name="game_bet_type_enum",
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
    )
    target_range_min: Mapped[int] = mapped_column(nullable=False)
    target_range_max: Mapped[int] = mapped_column(nullable=False)
    rolled_value: Mapped[int] = mapped_column(nullable=False)
    salt_left: Mapped[str] = mapped_column(Text, nullable=False)
    salt_right: Mapped[str] = mapped_column(Text, nullable=False)
    game_hash: Mapped[str] = mapped_column(Text, nullable=False)

    user_ref: Mapped[User] = relationship(foreign_keys=[user_id], lazy="raise")

    __table_args__ = (
        Index(
            "ix_games_user_id_created_at",
            user_id,
            created_at.desc()
        ),

        Index(
            "ix_games_created_at",
            created_at.desc()
        ),
    )


class SystemConfiguration(Base):
    __tablename__ = "system_configurations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=1)
    min_game_bet: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="1.00", nullable=False)
    is_maintenance_enabled: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)

    __table_args__ = (
        CheckConstraint("id = 1", name="single_row_configuration_constraint"),
    )
