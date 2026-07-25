from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.balance_service import IBalanceService
from src.domain.interfaces.cache_repo import ICacheRepository
from src.domain.interfaces.code_service import ICodeService
from src.domain.interfaces.user_repo import IUserRepository
from src.domain.interfaces.user_service import IUserService
from src.infrastructure.repositories.postgres.user_repo import UserRepository
from src.infrastructure.repositories.redis.cache_repo import CacheRepository
from src.services.auth_service import AuthService
from src.services.balance_service import BalanceService
from src.services.code_service import CodeService
from src.services.user_service import UserService


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            settings.async_database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_client(self) -> AsyncIterator[Redis]:
        client = from_url(settings.redis_url, decode_responses=True)
        yield client
        await client.aclose()

    @provide(scope=Scope.REQUEST)
    def provide_cache_gateway(self, redis: Redis) -> ICacheRepository:
        return CacheRepository(redis)


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> IUserRepository:
        return UserRepository(session)


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self, user_repo: IUserRepository, session: AsyncSession
    ) -> IAuthService:
        return AuthService(user_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_user_service(
        self, user_repo: IUserRepository, session: AsyncSession
    ) -> IUserService:
        return UserService(user_repo, session)

    @provide(scope=Scope.REQUEST)
    def get_balance_service(
        self, session: AsyncSession
    ) -> IBalanceService:
        return BalanceService(session)

    @provide(scope=Scope.REQUEST)
    def get_code_service(
        self, session: AsyncSession
    ) -> ICodeService:
        return CodeService(session)
