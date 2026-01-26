from html import escape
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.decorators import requires_registration
from services.users import set_nickname, validate_and_check_nickname, display_name

@requires_registration
async def setnick_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /setnick {new nickname}")
        return

    nickname = " ".join(context.args).strip()
    error = validate_and_check_nickname(chat_id, nickname)
    if error:
        await update.message.reply_text(error)
        return

    set_nickname(chat_id, user_id, nickname)
    await update.message.reply_text(
        f"Ваш новый никнейм: <b>{escape(nickname)}</b>",
        parse_mode="HTML"
    )

def get_profile_handlers():
    handlers = [
        CommandHandler("setnick", setnick_handler)
    ]
    return handlers
