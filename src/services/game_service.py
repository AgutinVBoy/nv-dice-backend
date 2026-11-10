import hashlib
import secrets
from decimal import Decimal, ROUND_HALF_EVEN

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ApiError
from src.core.i18n import t
from src.domain.dto.balance import BalanceChangeDTO
from src.domain.dto.game import GameBetDTO, GameResponseDTO, GameHashDTO, GameBaseDTO, GameResultDTO, GameHistoryDTO
from src.domain.entities.enums import GameBetType, TransactionDirection, TransactionType, GameResult
from src.domain.entities.models import Game, BalanceTransaction, UserBalance
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

    async def get_game_history(self, user_id: int, page: int, per_page: int) -> GameHistoryDTO:
        games = (await self.session.scalars(
            select(Game)
            .where(Game.user_id == user_id)
            .order_by(Game.created_at.desc(), Game.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page + 1)
        )).all()
        return GameHistoryDTO(
            items=games[:per_page],
            has_more=len(games) > per_page,
            page=page,
            per_page=per_page,
        )

    async def get_game_by_id(self, user_id: int, game_id: int, *, is_admin: bool = False) -> GameResultDTO:
        query = select(Game).where(Game.id == game_id)
        if not is_admin:
            query = query.where(Game.user_id == user_id)
        game = await self.session.scalar(query)
        if game is None:
            raise ApiError.not_found(t("ERR_GAME_RESULT_NOT_FOUND"))
        return GameResultDTO.model_validate(game)

    async def get_or_init_game(self, user_id: int) -> GameHashDTO:
        game = await self.cache_repository.get_game(user_id)
        if not game:
            game = generate_new_game()
            await self.cache_repository.create_new_game(user_id, game)
        return game

    async def process_game(self, user_id: int, game_bet: GameBetDTO) -> GameResponseDTO:
        # TODO: В редис при запуске складывать system_configuration (или читать напрямую из pg... Надо подумать над реализацией):
        #  1. При флаге is_maintenance_enabled не обрабатывать никакие запросы.
        #  2. Сравнивать ставку с минимальным значением не из схемы (там указано >=0), а из конфигурации - чтобы обновлять.

        query = select(UserBalance).where(UserBalance.user_id == user_id).with_for_update()
        user_balance: UserBalance | None = (await self.session.execute(query)).scalar_one_or_none()
        if not user_balance:
            raise ApiError.not_found(t("ERR_USER_NOT_FOUND", user_id=user_id))

        if user_balance.balance < game_bet.bet_amount:
            raise ApiError.conflict(t("ERR_BALANCE_NOT_ENOUGH"))

        game = await self.cache_repository.pop_game(user_id)
        if not game or game.game_hash != game_bet.game_hash:
            game = generate_new_game()
            await self.cache_repository.create_new_game(user_id, game)
            raise ApiError.conflict(t("ERR_GAME_NOT_FOUND"), details=[{"next_game": game.game_hash}])

        target_range_min = 0
        target_range_max = 999999
        match game_bet.bet_type:
            case GameBetType.OVER:
                target_range_min = int(10**6 * (100 - game_bet.probability) / 100)
            case GameBetType.UNDER:
                target_range_max = int(10**6 * game_bet.probability / 100 - 1)

        if target_range_min <= game.rolled_value <= target_range_max:
            game_result = GameResult.WIN
            win_amount = (game_bet.bet_amount * 100 / game_bet.probability).quantize(Decimal(".01"), rounding=ROUND_HALF_EVEN)
            balance_delta = win_amount - game_bet.bet_amount
            transaction_direction=TransactionDirection.CREDIT
        else:
            game_result = GameResult.LOSE
            win_amount = 0
            balance_delta = game_bet.bet_amount
            transaction_direction=TransactionDirection.DEBIT

        game_result = Game(
            user_id=user_id,
            result=game_result,
            bet_amount=game_bet.bet_amount,
            win_amount=win_amount,
            probability=game_bet.probability,
            bet_type=game_bet.bet_type,
            target_range_min=target_range_min,
            target_range_max=target_range_max,
            rolled_value=game.rolled_value,
            salt_left=game.salt_left,
            salt_right=game.salt_right,
            game_hash=game.game_hash
        )
        self.session.add(game_result)
        await self.session.flush()

        transaction_schema = await self.balance_service.update_balance(
            BalanceChangeDTO(
                amount=balance_delta,
                direction=transaction_direction,
                reason=TransactionType.GAME,
                user_id=user_id
            ),
            auto_commit=False
        )

        link_game_and_transaction_query = (
            update(BalanceTransaction)
            .where(BalanceTransaction.id == transaction_schema.transaction_id)
            .values(game_id=game_result.id)
        )
        await self.session.execute(link_game_and_transaction_query, execution_options={"synchronize_session": False})

        new_game = generate_new_game()
        await self.cache_repository.create_new_game(user_id, new_game)

        await self.session.commit()
        return GameResponseDTO(current_game=GameResultDTO.model_validate(game_result), next_game=new_game, new_balance=user_balance.balance)
