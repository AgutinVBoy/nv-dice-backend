import hashlib
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dto.game import GameBetDTO, GameResponseDTO, GameHashDTO, GameBaseDTO
from src.domain.interfaces.balance_service import IBalanceService
from src.domain.interfaces.cache_repo import ICacheRepository
from src.domain.interfaces.game_service import IGameService


def generate_new_game() -> GameBaseDTO:
    rolled_value = secrets.randbelow(10 ** 6)
    salt_left = secrets.token_urlsafe(8)
    salt_right = secrets.token_urlsafe(8)

    game_raw = f"{salt_left}:{rolled_value}:{salt_right}"
    game_hash = hashlib.sha512(game_raw.encode("utf-8")).hexdigest()

    return GameBaseDTO(
        game_hash=game_hash,
        salt_left=salt_left,
        salt_right=salt_right,
        rolled_value=rolled_value
    )


class GameService(IGameService):
    def __init__(self, balance_service: IBalanceService, cache_repository: ICacheRepository, session: AsyncSession):
        self.balance_service = balance_service
        self.cache_repository = cache_repository
        self.session = session

    async def get_or_init_game(self, user_id: int) -> GameHashDTO:
        game = await self.cache_repository.get_game(user_id)
        if not game:
            game = generate_new_game()
            await self.cache_repository.create_new_game(user_id, game)
        return game

    async def process_game(self, user_id: int, game_bet: GameBetDTO) -> GameResponseDTO:
        pass
