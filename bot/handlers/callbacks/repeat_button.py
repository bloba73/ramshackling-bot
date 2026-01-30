from telegram.ext import CallbackQueryHandler, ContextTypes
from types import SimpleNamespace
from utils.decorators import requires_no_active_session
from services.gamesessions import game_sessions
from handlers.conversation.solo_lobby import lobby_awaiting_bet as solo_lobby_bet
from handlers.conversation.multi_lobby import lobby_awaiting_bet as multi_lobby_bet

@requires_no_active_session
async def repeat_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    _, game_name, bet, owner_id = query.data.split(":")
    bet = int(bet)
    owner_id = int(owner_id)
    chat_id = query.message.chat.id

    if query.from_user.id != owner_id:
        await query.answer("Только владелец может повторить игру", show_alert=True)
        return

    await query.answer()

    mode = "duel" if game_name == "dices" else "solo"
    game_sessions.start(chat_id, owner_id, game_name, mode=mode)

    fake_message = SimpleNamespace(
        chat=query.message.chat,
        message_id=query.message.message_id,
        from_user=query.from_user,
        text=str(bet),
        reply_text=query.message.reply_text
    )
    fake_update = SimpleNamespace(
        effective_chat=query.message.chat,
        effective_user=query.from_user,
        message=fake_message
    )

    if game_name == "dices":
        await multi_lobby_bet(fake_update, context)
    else:
        await solo_lobby_bet(fake_update, context)


def get_repeat_handler():
    return CallbackQueryHandler(repeat_callback, pattern=r"^repeat:(slotmachine|coinflip|roulette|dices):\d+:\d+$")
