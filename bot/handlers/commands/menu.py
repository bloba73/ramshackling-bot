from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler
from utils.decorators import requires_no_active_session, requires_registration
from keyboards.inline import game_menu_keyboard
from services.users import display_name
from services.gamesessions import game_sessions

@requires_registration
@requires_no_active_session
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text(
        "Выберите вид игры:",
        reply_markup=game_menu_keyboard(user_id)
    )

@requires_registration
async def lobby_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    session = game_sessions.get(chat_id, user_id)
    if not session:
        await update.message.reply_text("Активная игра не найдена.")
        return

    owner_id = user_id
    msg_id = session.get("message_id")
    game_sessions.end(chat_id, owner_id)
    
    if msg_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=f"{display_name(chat_id, user_id)} отменил игру."
            )
        except:
            await update.message.reply_text(f"{display_name(chat_id, user_id)} отменил игру.")
    else:
        await update.message.reply_text(f"{display_name(chat_id, user_id)} отменил игру.")
    return ConversationHandler.END

def get_menu_handlers():
    handlers = [
        CommandHandler("menu", menu_handler),
        CommandHandler("cancelgame", lobby_cancel_command)
    ]
    return handlers
