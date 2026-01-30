from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackQueryHandler
from keyboards.inline import settings_buttons
from keyboards.reply import get_reply_keyboard

reply_keyboard_state = {}
replay_state = {}

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id

    try:
        _, setting_name, value = query.data.split(":")
        value = bool(int(value))
    except ValueError:
        await query.answer("Некорректные данные кнопки", show_alert=True)
        return

    if setting_name == "reply_keyboard":
        reply_keyboard_state[chat_id] = value
        if value:
            await context.bot.send_message(chat_id, "Клавиатура команд включена", reply_markup=get_reply_keyboard())
        else:
            await context.bot.send_message(chat_id, "Клавиатура команд отключена", reply_markup=ReplyKeyboardRemove())

    elif setting_name == "replay":
        replay_state[chat_id] = value
        await context.bot.send_message(
            chat_id,
            f"Кнопка повторить {'включена' if value else 'выключена'}"
        )

    await query.edit_message_reply_markup(reply_markup=settings_buttons(
        reply_current=reply_keyboard_state.get(chat_id, False),
        replay_current=replay_state.get(chat_id, False)
    ))
    await query.answer()


def is_reply_keyboard_enabled(chat_id: int) -> bool:
    return reply_keyboard_state.get(chat_id, False)


def is_replay_enabled(chat_id: int) -> bool:
    return replay_state.get(chat_id, False)


def get_settings_handlers():
    return [
        CallbackQueryHandler(settings_callback, pattern=r"^settings:(reply_keyboard|replay):\d$")
    ]
