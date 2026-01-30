from html import escape
import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from keyboards.inline import settings_buttons
from handlers.callbacks.settings import reply_keyboard_state
from services.leaderboard import VALID_SORT_PARAMS, get_leaderboard

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>Доступные команды:</b>\n\n"
        "— <b>Для всех пользователей:</b>\n"
        "/help — показать список команд\n"
        "/registration — зарегистрироваться в боте\n"
        "/leaderboard — показать текущий лидерборд\n"
        "/id — узнать ID пользователя, на чьё сообщение вы ответили\n"
        "/gameinfo — информация о играх\n"
        "/settings — настройки бота\n"
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


async def gameinfo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>Доступные игры</b>\n\n"

        "<b>🪙 Coinflip</b>\n"
        "Классический выбор стороны монеты.\n\n"
        "• Выберите: <b>Орёл</b> или <b>Решка</b>\n"
        "• Бот подбрасывает монету\n"
        "• Если угадали — выигрываете\n\n"
        "Множитель выигрыша: <b>x1.5</b>\n\n"

        "<b>🎰 Slot Machine</b>\n"
        "Однорукий бандит — всё решает удача.\n\n"
        "• Бот крутит слот-машину\n"
        "• Выпавшие комбинации определяют выигрыш\n\n"
        "Возможные множители:\n"
        "• <b>x2, x3, x4</b> — редкие комбинации\n"
        "• <b>x7</b> — джекпот🍕\n\n"

        "<b>⚙️ Русская рулетка</b>\n"
        "Опасная игра на жадность.\n\n"
        "• В барабане 6 камор\n"
        "• Игра начинается с 1 патрона\n"
        "• На каждом этапе можно <b>выстрелить</b> или <b>уйти</b>\n"
        "• Чем дальше — тем выше риск и награда\n\n"
        "Множители:\n"
        "• 1 патрон — <b>x1.2</b>\n"
        "• 2 патрона — <b>x1.5</b>\n"
        "• 3 патрона — <b>x2.0</b>\n"
        "• 4 патрона — <b>x2.25</b>\n"
        "• 5 патронов — <b>x3.0</b>\n\n"
        "Один неудачный выстрел — и ставка потеряна.\n\n"

        "<b>🎲 Dices</b>\n"
        "Игра на броски кубиков против другого игрока.\n\n"
        "• Создайте лобби и введите ставку\n"
        "• Другой игрок присоединяется к игре\n"
        "• Каждый игрок кидает кубик\n"
        "• Игрок с большим числом выигрывает и забирает ставку соперника\n"
        "• При ничьей ставка остаётся при игроке, ничья — без потерь\n\n"
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


async def z_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sticker_set = await context.bot.get_sticker_set("GOIDA_LUTAYA")
        stickers = sticker_set.stickers
        if not stickers:
            await update.message.reply_text("Стикеры в паке не найдены.")
            return

        sticker = random.choice(stickers)
        await update.message.reply_sticker(sticker.file_id)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при отправке стикера: {e}")


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    current = reply_keyboard_state.get(chat_id, False)
    
    await update.message.reply_text(
        "Временные настройки:",
        reply_markup=settings_buttons(current)
    )


def get_common_handlers():
    handlers = [
        CommandHandler("help", help_handler),
        CommandHandler("leaderboard", leaderboard_handler),
        CommandHandler("id", id_handler),
        CommandHandler("gameinfo", gameinfo_handler),
        CommandHandler("settings", settings_handler),
        CommandHandler("z", z_handler)
    ]
    return handlers