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
        _, _, _, game_name, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return ConversationHandler.END
    
    if user_id != owner_id:
        await query.answer("Это не ваше меню", show_alert=True)
        return ConversationHandler.END
    
    game_sessions.start(chat_id, user_id, game_name, mode="solo")

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
    
    await run_game(chat_id, user_id, bet, context)

    return ConversationHandler.END


async def run_game(chat_id: int, user_id: int, bet: int, context: ContextTypes.DEFAULT_TYPE):
    session = game_sessions.get(chat_id, user_id)

    if not session:
        await context.bot.send_message(chat_id, "Ошибка: активная игра не найдена.")
        return

    game_name = session["game"]

    if game_name == "coinflip":
        game = Coinflip(chat_id, user_id, bet)
        await game.play(None, context)

    game_sessions.end(chat_id, user_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = game_sessions.get(chat_id, user_id)
    if session and session["owner_id"] == user_id:
        game_sessions.end(chat_id, user_id)

    await update.message.reply_text("Игра отменена.")
    return ConversationHandler.END


def get_solo_lobby_handler():
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                lobby_entry,
                pattern=r"^menu:single:play:[^:]+:\d+$"
            )
        ],
        states={
            States.AWAITING_BET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, lobby_awaiting_bet)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        allow_reentry=True
    )


