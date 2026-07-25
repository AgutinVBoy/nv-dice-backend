from abc import ABC, abstractmethod

from src.domain.dto.game import GameBaseDTO


class ICacheRepository(ABC):
    @abstractmethod
    async def create_new_game(self, user_id: int, game_data: GameBaseDTO) -> None:
        ...

    @abstractmethod
    async def get_game(self, user_id: int) -> GameBaseDTO | None:
        ...

    @abstractmethod
    async def pop_game(self, user_id: int) -> GameBaseDTO | None:
        ...
