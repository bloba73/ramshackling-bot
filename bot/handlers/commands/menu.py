from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.decorators import requires_registration
from keyboards.inline import game_menu_keyboard


@requires_registration
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text(
        "Выберите вид игры:",
        reply_markup=game_menu_keyboard(user_id)
    )


def get_menu_handlers():
    handlers = [
        CommandHandler("menu", menu_handler)
    ]
    return handlers
