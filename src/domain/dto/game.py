from pydantic import BaseModel, Field, ConfigDict

from src.domain.dto.balance import Balance
from src.domain.dto.common import CustomDateTime
from src.domain.entities.enums import GameBetType, GameResult


class GameHashDTO(BaseModel):
    game_hash: str

class GameBaseDTO(GameHashDTO):
    salt_left: str
    salt_right: str
    rolled_value: int = Field(ge=0, le=999999)


class GameBetDTO(GameHashDTO):
    bet_amount: Balance
    bet_type: GameBetType
    probability: int = Field(ge=1, le=95)


class GameResultDTO(GameBaseDTO, GameBetDTO):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: CustomDateTime
    result: GameResult
    win_amount: Balance
    target_range_min: int = Field(ge=0, le=999999)
    target_range_max: int = Field(ge=0, le=999999)


class GameResponseDTO(BaseModel):
    current_game: GameResultDTO
    next_game: GameHashDTO
    new_balance: Balance
