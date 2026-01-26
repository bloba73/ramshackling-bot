from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from keyboards.inline import (
    game_menu_keyboard,
    solo_game_mode_keyboard,
    duel_game_mode_keyboard,
)
from utils.decorators import handle_telegram_errors

@handle_telegram_errors
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return
    
    await query.answer()
    
    try:
        prefix, section, action, owner_id = query.data.split(":")
        owner_id = int(owner_id)
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return
    
    if query.from_user.id != owner_id:
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
            reply_markup=solo_game_mode_keyboard(query.from_user.id)
        )
        return

    if section == "duel" and action == "open":
        await query.edit_message_text(
            "Выбран режим: <b>Дуэльная игра</b>",
            parse_mode="HTML",
            reply_markup=duel_game_mode_keyboard(query.from_user.id)
        )
        return
    
    if section == "single":
        await handle_single_game_selection(query, action)
        return

    if section == "duel":
        await handle_duel_game_selection(query, action)
        return
    
    await query.answer("Неизвестное действие", show_alert=True)
 
   
async def handle_single_game_selection(query, action: str):
    if action == "p1":
        await query.answer("Одиночная игра: режим P1", show_alert=True)
        return

    if action == "p2":
        await query.answer("Одиночная игра: режим P2", show_alert=True)
        return

    await query.answer("Неизвестный режим одиночной игры", show_alert=True)

 
async def handle_duel_game_selection(query, action: str):
    if action == "p1":
        await query.answer("Дуэльная игра: режим P1", show_alert=True)
        return

    if action == "p2":
        await query.answer("Дуэльная игра: режим P2", show_alert=True)
        return

    await query.answer("Неизвестный режим дуэльной игры", show_alert=True)


def get_menu_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(menu_callback, pattern=r"^menu:")
