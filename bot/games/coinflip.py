import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.transactions import add_balance, subtract_balance
from services.gamesessions import game_sessions

class Coinflip:
    def __init__(self, chat_id: int, user_id: int, bet: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.bet = bet
        self.choice = None
        self.message_id = None


    async def play(self, context: ContextTypes.DEFAULT_TYPE):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ОРЁЛ", callback_data="coinflip:choice:Орёл")],
            [InlineKeyboardButton("РЕШКА", callback_data="coinflip:choice:Решка")]
        ])
        msg = await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"Выберите сторону монетки. \nСтавка: {self.bet} Ɍ",
            reply_markup=keyboard
        )
        self.message_id = msg.message_id
        session = game_sessions.get(self.chat_id, self.user_id)
        if session:
            session["message_id"] = self.message_id


    async def handle_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        chat_id = query.message.chat.id

        if user_id != self.user_id:
            await query.answer("Это не ваш выбор!", show_alert=True)
            return

        _, _, choice = query.data.split(":")
        self.choice = choice

        await query.edit_message_text(
            f"Выбор игрока: <b>{self.choice}</b>",
            parse_mode="HTML"
        )

        await asyncio.sleep(1)

        await context.bot.send_message(self.chat_id, "Бот подкидывает монетку...")

        await asyncio.sleep(1)

        result = random.choice(["Орёл", "Решка"])

        if self.choice == result:
            add_balance(self.chat_id, self.user_id, self.bet)
            outcome_text = f"Поздравляем! Вы выиграли <b>{self.bet} Ɍ</b>"
        else:
            subtract_balance(self.chat_id, self.user_id, self.bet)
            outcome_text = f"Вы проиграли <b>{self.bet} Ɍ</b>"

        await context.bot.send_message(
            self.chat_id,
            f"Результат: <b>{result}</b>\n{outcome_text}",
            parse_mode="HTML"
        )

        game_sessions.end(chat_id, user_id)


async def coinflip_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = game_sessions.get(chat_id, user_id)
    if not session or "game_instance" not in session:
        await query.answer("Сессия игры не найдена", show_alert=True)
        return

    game = session["game_instance"]
    await game.handle_choice(update, context)


def get_coinflip_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(coinflip_callback, pattern=r"^coinflip:choice:(Орёл|Решка)$")