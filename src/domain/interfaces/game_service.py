from abc import ABC, abstractmethod

from src.domain.dto.game import GameHashDTO, GameBetDTO, GameResponseDTO


class IGameService(ABC):
    @abstractmethod
    async def get_or_init_game(self, user_id: int) -> GameHashDTO:
        ...

    @abstractmethod
    async def process_game(self, user_id: int, game_bet: GameBetDTO) -> GameResponseDTO:
        ...
