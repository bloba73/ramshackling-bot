import asyncio
from telegram.ext import ContextTypes
from services.transactions import add_balance, subtract_balance
from services.gamesessions import game_sessions
from services.users import update_user_meta
from services.users import display_name
from keyboards.inline import repeat_button
from handlers.callbacks.settings import is_replay_enabled

class Dices:
    def __init__(self, chat_id: int, owner_id: int, joiner_id: int, bet: int):
        self.chat_id = chat_id
        self.owner_id = owner_id
        self.joiner_id = joiner_id
        self.bet = bet

    async def play(self, update, context: ContextTypes.DEFAULT_TYPE):
        owner_name = display_name(self.chat_id, self.owner_id)
        joiner_name = display_name(self.chat_id, self.joiner_id)

        await context.bot.send_message(
            self.chat_id,
            f"🎲 <b>{owner_name}</b> бросает кубик...",
            parse_mode="HTML"
        )

        dice_owner = await context.bot.send_dice(
            chat_id=self.chat_id,
            emoji="🎲"
        )

        owner_value = dice_owner.dice.value

        await asyncio.sleep(3)

        await context.bot.send_message(
            self.chat_id,
            f"🎲 <b>{joiner_name}</b> бросает кубик...",
            parse_mode="HTML"
        )

        dice_joiner = await context.bot.send_dice(
            chat_id=self.chat_id,
            emoji="🎲"
        )

        joiner_value = dice_joiner.dice.value

        await asyncio.sleep(3)

        if owner_value > joiner_value:
            add_balance(self.chat_id, self.owner_id, self.bet)
            subtract_balance(self.chat_id, self.joiner_id, self.bet)

            result_text = (
                f"Победил <b>{owner_name}</b>\n"
                f"{owner_value} vs {joiner_value}\n"
                f"+{self.bet} Ɍ"
            )

            update_user_meta(
                self.chat_id,
                self.owner_id,
                games_played=lambda old: (old or 0) + 1,
                total_wins=lambda old: (old or 0) + 1,
                max_amount_won=lambda old: max(old or 0, self.bet)
            )
            update_user_meta(
                self.chat_id,
                self.joiner_id,
                games_played=lambda old: (old or 0) + 1,
                total_losses=lambda old: (old or 0) + 1,
                max_amount_lost=lambda old: max(old or 0, self.bet)
            )

        elif joiner_value > owner_value:
            add_balance(self.chat_id, self.joiner_id, self.bet)
            subtract_balance(self.chat_id, self.owner_id, self.bet)

            result_text = (
                f"Победил <b>{joiner_name}</b>\n"
                f"{owner_value} vs {joiner_value}\n"
                f"+{self.bet} Ɍ"
            )

            update_user_meta(
                self.chat_id,
                self.joiner_id,
                games_played=lambda old: (old or 0) + 1,
                total_wins=lambda old: (old or 0) + 1,
                max_amount_won=lambda old: max(old or 0, self.bet)
            )
            update_user_meta(
                self.chat_id,
                self.owner_id,
                games_played=lambda old: (old or 0) + 1,
                total_losses=lambda old: (old or 0) + 1,
                max_amount_lost=lambda old: max(old or 0, self.bet)
            )

        else:
            result_text = (
                f"Ничья\n"
                f"{owner_value} = {joiner_value}\n"
                f"Ставки возвращены"
            )

            update_user_meta(
                self.chat_id,
                self.owner_id,
                games_played=lambda old: (old or 0) + 1,
                total_draws=lambda old: (old or 0) + 1
            )
            update_user_meta(
                self.chat_id,
                self.joiner_id,
                games_played=lambda old: (old or 0) + 1,
                total_draws=lambda old: (old or 0) + 1
            )

        if is_replay_enabled(self.chat_id):
            markup = repeat_button(self.chat_id, self.user_id, self.bet, "dices")
        else:
            markup = None

        await context.bot.send_message(
            self.chat_id,
            result_text,
            parse_mode="HTML",
            reply_markup=markup
        )

        game_sessions.end(self.chat_id, self.owner_id)
