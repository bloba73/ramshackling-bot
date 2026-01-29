from telegram import Update
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from games.coinflip import Coinflip
from utils.decorators import requires_no_active_session
from services.states import States
from services.users import display_name
from services.transactions import has_balance
from services.gamesessions import game_sessions


@requires_no_active_session
async def lobby_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    await query.answer()

    try:
        _, _, game_name, owner_id = query.data.split(":")
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return
    
    game_sessions.start(chat_id, user_id, game_name)

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
    
    await lobby_awaiting_game_results(update, chat_id, user_id, bet, context)

    return ConversationHandler.END


async def lobby_awaiting_game_results(update: Update, chat_id: int, user_id: int, bet: int, context: ContextTypes.DEFAULT_TYPE):    
    game_name = game_sessions.get(chat_id, user_id, {}).get("game")

    if game_name is None:
        await update.message.reply_text("Ошибка: активная сессия не найдена.")
        return

    if game_name == "coinflip":
        game = Coinflip(chat_id, user_id, bet)
        await game.play(None, context)

    game_sessions.end(chat_id, user_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if game_sessions.get(chat_id, user_id):
        game_sessions.end(chat_id, user_id)

    await update.message.reply_text("Игра отменена.")
    return ConversationHandler.END


def get_lobby_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                lobby_entry,
                pattern=r"^menu:single:coinflip:\d+$"
            )
        ],
        states={
            States.AWAITING_BET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lobby_awaiting_bet)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )


