from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from games.dices import Dices
from services.states import States
from services.users import display_name
from services.transactions import has_balance
from services.gamesessions import game_sessions
from utils.decorators import requires_no_active_session
from keyboards.inline import duel_lobby_keyboard

@requires_no_active_session
async def lobby_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    await query.answer()

    try:
        _, _, _, game_name, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return ConversationHandler.END

    if user_id != owner_id:
        await query.answer("Это не ваше меню", show_alert=True)
        return ConversationHandler.END

    game_sessions.start(
        chat_id,
        user_id,
        game_name,
        mode="duel"
    )

    await query.edit_message_text(
        f"{display_name(chat_id, user_id)} выбрал игру: <b>{game_name.capitalize()}</b>",
        parse_mode="HTML"
    )

    await query.message.reply_text("Введите ставку:")
    return States.AWAITING_BET


async def lobby_awaiting_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    try:
        bet = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Введите число.")
        return States.AWAITING_BET

    if bet <= 0:
        await update.message.reply_text("Ставка должна быть больше 0.")
        return States.AWAITING_BET

    if not has_balance(chat_id, user_id, bet):
        await update.message.reply_text("Недостаточно средств.")
        return States.AWAITING_BET

    session = game_sessions.get(chat_id, user_id)
    if not session:
        await update.message.reply_text("Сессия не найдена.")
        return ConversationHandler.END

    session["bet"] = bet
    session["players"] = [user_id]

    message = await update.message.reply_text(
        f"{display_name(chat_id, user_id)} ждёт соперника\n"
        f"Игра: <b>{session['game'].capitalize()}</b>\n"
        f"Ставка: <b>{bet}</b>",
        parse_mode="HTML",
        reply_markup=duel_lobby_keyboard(user_id)
    )

    session["message_id"] = message.message_id

    return ConversationHandler.END


async def lobby_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    joiner_id = query.from_user.id

    await query.answer()

    try:
        _, _, action, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        return

    if joiner_id == owner_id:
        await query.answer("Нельзя играть самому с собой", show_alert=True)
        return

    session = game_sessions.get(chat_id, owner_id)
    if not session:
        await query.edit_message_text("Лобби больше не существует.")
        return

    bet = session["bet"]

    if not has_balance(chat_id, joiner_id, bet):
        await query.answer("Недостаточно средств", show_alert=True)
        return

    session["players"].append(joiner_id)

    await query.edit_message_text(
        f"Дуэль началась!\n\n"
        f"{display_name(chat_id, owner_id)} vs {display_name(chat_id, joiner_id)}\n"
        f"Ставка: <b>{bet}</b>",
        parse_mode="HTML"
    )

    session = game_sessions.get(chat_id, owner_id)

    if not session:
        await context.bot.send_message(chat_id, "Ошибка: активная игра не найдена.")
        return

    game_name = session["game"]

    if game_name == "dices":
        game = Dices(chat_id, owner_id, joiner_id, bet)
        await game.play(None, context)

    game_sessions.end(chat_id, owner_id)


async def lobby_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    await query.answer()

    try:
        _, mode, action, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        return

    if user_id != owner_id:
        await query.answer("Отменить может только создатель", show_alert=True)
        return

    game_sessions.end(chat_id, owner_id)

    await query.edit_message_text(
        f"{display_name(chat_id, user_id)} отменил игру."
    )


def get_multi_lobby_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                lobby_entry,
                pattern=r"^menu:duel:play:[^:]+:\d+$"
            )
        ],
        states={
            States.AWAITING_BET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lobby_awaiting_bet)
            ]
        },
        fallbacks=[CommandHandler("cancel", lobby_cancel)],
        allow_reentry=True,
    )


def get_multi_lobby_callbacks():
    return [
        CallbackQueryHandler(
            lobby_join,
            pattern=r"^lobby:duel:join:\d+$"
        ),
        CallbackQueryHandler(
            lobby_cancel,
            pattern=r"^lobby:duel:cancel:\d+$"
        ),
    ]