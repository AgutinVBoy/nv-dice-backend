from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.models import User
from src.domain.interfaces.user_repo import IUserRepository


class UserRepository(IUserRepository):
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id).options(
            joinedload(User.role_ref),
            joinedload(User.balance_ref)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username).options(
            joinedload(User.role_ref),
            joinedload(User.balance_ref)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User) -> User:
        updated_user = await self.session.merge(user)
        await self.session.flush()
        return updated_user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()
