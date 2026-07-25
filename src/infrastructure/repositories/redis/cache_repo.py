from redis.asyncio import Redis

from src.domain.dto.game import GameBaseDTO
from src.domain.interfaces.cache_repo import ICacheRepository


def _get_redis_game_key(user_id: int) -> str:
    return f"user:{user_id}:game"


class CacheRepository(ICacheRepository):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.ttl_seconds = 3600

    async def create_new_game(self, user_id: int, game_data: GameBaseDTO) -> None:
        await self.redis.set(_get_redis_game_key(user_id), game_data.model_dump_json(), self.ttl_seconds)

    async def get_game(self, user_id: int) -> GameBaseDTO | None:
        raw_data = await self.redis.get(_get_redis_game_key(user_id))
        if raw_data is None:
            return None
        return GameBaseDTO.model_validate_json(raw_data)

    async def pop_game(self, user_id: int) -> GameBaseDTO | None:
        raw_data = await self.redis.getdel(_get_redis_game_key(user_id))
        if raw_data is None:
            return None
        return GameBaseDTO.model_validate_json(raw_data)
