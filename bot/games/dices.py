import asyncio
from telegram.ext import ContextTypes
from services.transactions import add_balance, subtract_balance
from services.gamesessions import game_sessions
from services.users import display_name

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

        elif joiner_value > owner_value:
            add_balance(self.chat_id, self.joiner_id, self.bet)
            subtract_balance(self.chat_id, self.owner_id, self.bet)

            result_text = (
                f"Победил <b>{joiner_name}</b>\n"
                f"{owner_value} vs {joiner_value}\n"
                f"+{self.bet} Ɍ"
            )

        else:
            result_text = (
                f"Ничья\n"
                f"{owner_value} = {joiner_value}\n"
                f"Ставки возвращены"
            )

        await context.bot.send_message(
            self.chat_id,
            result_text,
            parse_mode="HTML"
        )

        game_sessions.end(self.chat_id, self.owner_id)
