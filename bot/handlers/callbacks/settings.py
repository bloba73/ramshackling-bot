from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackQueryHandler
from keyboards.inline import settings_buttons
from keyboards.reply import get_reply_keyboard

reply_keyboard_state = {}
# replay_state = {}

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id

    try:
        _, setting_name, value = query.data.split(":")
        value = bool(int(value))
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return

    reply_keyboard_state[chat_id] = value

    if value:
        await context.bot.send_message(chat_id, "Клавиатура включена", reply_markup=get_reply_keyboard())
    else:
        await context.bot.send_message(chat_id, "Клавиатура отключена", reply_markup=ReplyKeyboardRemove())

    await query.edit_message_reply_markup(reply_markup=settings_buttons(value))
    await query.answer(f"Клавиатура команд: {'включена' if value else 'выключена'}")


def is_reply_keyboard_enabled(chat_id: int) -> bool:
    return reply_keyboard_state.get(chat_id, False)


def get_settings_handlers():
    return [
        CallbackQueryHandler(settings_callback, pattern=r"^settings:reply_keyboard:\d$")
    ]