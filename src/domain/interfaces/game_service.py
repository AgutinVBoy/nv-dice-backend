from abc import ABC, abstractmethod

from src.domain.dto.game import GameHashDTO, GameBetDTO, GameResponseDTO, GameHistoryDTO, GameResultDTO


class IGameService(ABC):
    @abstractmethod
    async def get_game_history(self, user_id: int, page: int, per_page: int) -> GameHistoryDTO:
        ...

    @abstractmethod
    async def get_game_by_id(self, user_id: int, game_id: int, *, is_admin: bool = False) -> GameResultDTO:
        ...

    @abstractmethod
    async def get_or_init_game(self, user_id: int) -> GameHashDTO:
        ...

    @abstractmethod
    async def process_game(self, user_id: int, game_bet: GameBetDTO) -> GameResponseDTO:
        ...
