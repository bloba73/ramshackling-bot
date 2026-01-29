from html import escape
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from services.leaderboard import VALID_SORT_PARAMS, get_leaderboard

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>Доступные команды:</b>\n\n"
        "— <b>Для всех пользователей:</b>\n"
        "/help — показать список команд\n"
        "/registration — зарегистрироваться в боте\n"
        "/leaderboard — показать текущий лидерборд\n"
        "/id — узнать ID пользователя, на чьё сообщение вы ответили\n"
        "/cancel — отменить текущую команду\n\n"
        
        "— <b>Для зарегистрированных пользователей:</b>\n"
        "/menu — открыть меню с играми\n"
        "/cancelgame — отменяет все активные игровые сессии или лобби\n"
        "/balance — показать ваш текущий баланс\n"
        "/give {user} {amount} — передать {amount} ремшекелей другому пользователю\n"
        "/drop {amount} — выбросить {amount} ремшекелей\n"
        "/setnick {new nickname} — изменить никнейм вашего аккаунта\n"
        "/deleteaccount — удалить зарегистрированный аккаунт\n\n"
        
        "— <b>Для создателя чата:</b>\n"
        "/grant {user} {amount} — выдать {amount} ремшекелей пользователю\n"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )


async def leaderboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sort_by = context.args[0] if context.args and context.args[0] in VALID_SORT_PARAMS else "balance"

    leaderboard = get_leaderboard(chat_id, limit=10, sort_by=sort_by)
    if not leaderboard:
        await update.message.reply_text("Пока нет зарегистрированных пользователей.")
        return

    text = f"<b>Лидерборд по {sort_by}:</b>\n"
    for i, user in enumerate(leaderboard, start=1):
        value = user.get(sort_by, 0)
        suffix = " Ɍ" if sort_by == "balance" else ""
        text += f"{i}. {escape(user['display_name'])} — {value}{suffix}\n"

    await update.message.reply_text(text, parse_mode="HTML")


async def id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text("Ответьте на сообщение пользователя, чтобы узнать его ID.")
        return

    target_user = reply.from_user
    await update.message.reply_text(f"ID пользователя: `{target_user.id}`", parse_mode="Markdown")


def get_common_handlers():
    handlers = [
        CommandHandler("help", help_handler),
        CommandHandler("leaderboard", leaderboard_handler),
        CommandHandler("id", id_handler)
    ]
    return handlers