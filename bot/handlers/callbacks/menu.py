from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from services.users import display_name
from services.states import States
from keyboards.inline import (
    game_menu_keyboard,
    solo_game_mode_keyboard,
    duel_game_mode_keyboard,
)
from utils.decorators import handle_telegram_errors

@handle_telegram_errors
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    if not query or not query.data:
        return
    
    await query.answer()
    
    try:
        prefix, section, action, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return
    
    if user_id != owner_id:
        await query.answer("Это меню не для вас", show_alert=True)
        return


    if section == "root" and action == "open":
        await query.edit_message_text(
            "Выберите вид игры:",
            reply_markup=game_menu_keyboard(owner_id)
        )
        return

    if section == "single" and action == "open":
        await query.edit_message_text(
            "Выбран режим: <b>Одиночная игра</b>",
            parse_mode="HTML",
            reply_markup=solo_game_mode_keyboard(user_id)
        )
        return

    if section == "duel" and action == "open":
        await query.edit_message_text(
            "Выбран режим: <b>Дуэльная игра</b>",
            parse_mode="HTML",
            reply_markup=duel_game_mode_keyboard(user_id)
        )
        return


def get_menu_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(menu_callback, pattern=r"^menu:")
