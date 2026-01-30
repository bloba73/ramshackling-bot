import random
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.users import update_user_meta
from services.transactions import add_balance, subtract_balance
from services.gamesessions import game_sessions
from keyboards.inline import repeat_button
from handlers.callbacks.settings import is_replay_enabled


class Roulette:
    MAX_CHAMBERS = 6

    MULTIPLIERS = {
        1: 1,
        2: 1.2,
        3: 1.5,
        4: 2.25,
        5: 3.5,
    }

    def __init__(self, chat_id: int, user_id: int, bet: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.bet = bet
        self.bullets = 1
        self.message_id = None

    def _text(self) -> str:
        if self.bullets == 1:
            return (
                f"<b>Русская рулетка</b>\n\n"
                f"Патронов в барабане: <b>{self.bullets}</b> из {self.MAX_CHAMBERS}\n"
                f"Ставка: <b>{self.bet} Ɍ</b>"
            )

        multiplier = self.MULTIPLIERS.get(self.bullets, 1)
        return (
            f"<b>Русская рулетка</b>\n\n"
            f"Патронов в барабане: <b>{self.bullets}</b> из {self.MAX_CHAMBERS}\n"
            f"Множитель выигрыша: <b>x{multiplier}</b>"
        )

    def _keyboard(self) -> InlineKeyboardMarkup | None:
        buttons = []

        if self.bullets <= 3:
            buttons.append(InlineKeyboardButton("Выстрелить", callback_data="roulette:shoot"))
            buttons.append(InlineKeyboardButton("Уйти", callback_data="roulette:cancel"))

        elif self.bullets >= 4:
            buttons.append(InlineKeyboardButton("Выстрелить", callback_data="roulette:shoot"))
            buttons.append(InlineKeyboardButton("Забрать", callback_data="roulette:take"))

        if not buttons:
            return None

        return InlineKeyboardMarkup([[b] for b in buttons])


    async def play(self, context: ContextTypes.DEFAULT_TYPE):
        msg = await context.bot.send_message(
            chat_id=self.chat_id,
            text=self._text(),
            reply_markup=self._keyboard(),
            parse_mode="HTML",
        )

        self.message_id = msg.message_id

        session = game_sessions.get(self.chat_id, self.user_id)
        if session:
            session["message_id"] = self.message_id
            session["game_instance"] = self


    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query

        if query.from_user.id != self.user_id:
            await query.answer("Это не ваша игра", show_alert=True)
            return

        action = query.data.split(":")[1]

        if action == "cancel":
            await self._cancel(query)
        elif action == "take":
            await self._take(query)
        elif action == "shoot":
            await self._shoot(query)


    async def _cancel(self, query):
        await query.edit_message_text("Игра отменена")
        update_user_meta(
            self.chat_id,
            self.user_id,
        )
        game_sessions.end(self.chat_id, self.user_id)

    async def _take(self, query):
        multiplier = self.MULTIPLIERS[self.bullets]
        win = math.ceil(self.bet * multiplier)

        add_balance(self.chat_id, self.user_id, win)

        markup = repeat_button(self.chat_id, self.user_id, self.bet, "roulette") if is_replay_enabled(self.chat_id) else None

        await query.edit_message_text(
            f"<b>Вы забрали выигрыш!</b>\n\n"
            f"Множитель: x{multiplier}\n"
            f"Получено: <b>{win} Ɍ</b>",
            parse_mode="HTML",
            reply_markup=markup
        )

        update_user_meta(
            self.chat_id,
            self.user_id,
            games_played=lambda old: (old or 0) + 1,
            total_wins=lambda old: (old or 0) + 1,
            max_amount_won=lambda old: max(old or 0, win),
        )

        game_sessions.end(self.chat_id, self.user_id)

    async def _shoot(self, query):
        if random.randint(1, self.MAX_CHAMBERS) <= self.bullets:
            subtract_balance(self.chat_id, self.user_id, self.bet)

            markup = repeat_button(self.chat_id, self.user_id, self.bet, "roulette") if is_replay_enabled(self.chat_id) else None

            await query.edit_message_text(
                f"<b>Выстрел!</b>\n\n"
                f"Вы проиграли <b>{self.bet} Ɍ</b>",
                parse_mode="HTML",
                reply_markup=markup
            )

            update_user_meta(
                self.chat_id,
                self.user_id,
                games_played=lambda old: (old or 0) + 1,
                total_losses=lambda old: (old or 0) + 1,
                max_amount_lost=lambda old: max(old or 0, self.bet),
            )

            game_sessions.end(self.chat_id, self.user_id)
            return

        if self.bullets == 5:
            multiplier = self.MULTIPLIERS[self.bullets]
            win = math.ceil(self.bet * multiplier)

            add_balance(self.chat_id, self.user_id, win)

            markup = repeat_button(self.chat_id, self.user_id, self.bet, "roulette") if is_replay_enabled(self.chat_id) else None

            await query.edit_message_text(
                f"<b>Невероятно!</b>\n\n"
                f"Вы победили!\n"
                f"Множитель: x{multiplier}\n"
                f"Получено: <b>{win} Ɍ</b>",
                parse_mode="HTML",
                reply_markup=markup
            )

            update_user_meta(
                self.chat_id,
                self.user_id,
                games_played=lambda old: (old or 0) + 1,
                total_wins=lambda old: (old or 0) + 1,
                max_amount_won=lambda old: max(old or 0, win),
            )

            game_sessions.end(self.chat_id, self.user_id)
            return
        
        self.bullets += 1

        await query.edit_message_text(
            self._text(),
            reply_markup=self._keyboard(),
            parse_mode="HTML",
        )


async def roulette_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    session = game_sessions.get(chat_id, user_id)
    if not session or "game_instance" not in session:
        await query.answer("Игра не найдена", show_alert=True)
        return

    await session["game_instance"].handle(update, context)


def get_roulette_handler():
    return CallbackQueryHandler(
        roulette_callback,
        pattern=r"^roulette:(shoot|cancel|take)$",
    )
