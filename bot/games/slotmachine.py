import asyncio
from telegram.ext import ContextTypes
from services.transactions import add_balance, subtract_balance
from services.gamesessions import game_sessions
from services.users import update_user_meta

class SlotMachine:
    MULTIPLIERS = {
        1: 2,
        22: 3,
        43: 4,
        64: 7
    }

    def __init__(self, chat_id: int, user_id: int, bet: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.bet = bet

    async def play(self, context: ContextTypes.DEFAULT_TYPE):

        dice_msg = await context.bot.send_dice(
            chat_id=self.chat_id,
            emoji="🎰"
        )

        await asyncio.sleep(3)

        result = dice_msg.dice.value
        multiplier = self.MULTIPLIERS.get(result, 0)

        if multiplier > 0:
            winnings = self.bet * multiplier
            add_balance(self.chat_id, self.user_id, winnings)
            outcome_text = f"Везёт! Вы выиграли {winnings} Ɍ (x{multiplier})"

            update_user_meta(
                self.chat_id,
                self.user_id,
                games_played=lambda old: (old or 0) + 1,
                total_wins=lambda old: (old or 0) + 1,
                max_amount_won=lambda old: max(old or 0, winnings)
            )

        else:
            subtract_balance(self.chat_id, self.user_id, self.bet)
            outcome_text = f"Увы, вы проиграли {self.bet} Ɍ"

            update_user_meta(
                self.chat_id,
                self.user_id,
                games_played=lambda old: (old or 0) + 1,
                total_wins=lambda old: (old or 0) + 1,
                max_amount_won=lambda old: max(old or 0, winnings)
            )

        await context.bot.send_message(
            self.chat_id,
            f"{outcome_text}",
            parse_mode="HTML"
        )

        game_sessions.end(self.chat_id, self.user_id)
