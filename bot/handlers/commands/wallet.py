from html import escape
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.decorators import requires_creator, requires_registration
from services.transactions import get_balance, has_balance, add_balance, subtract_balance, transfer
from services.users import display_name, get_user_by_identifier


@requires_registration
async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    balance = get_balance(chat_id, user_id)
    await update.message.reply_text(f"Ваш текущий баланс: <b>{balance} Ɍ</b>", parse_mode="HTML")


@requires_registration
async def give_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    from_user = update.effective_user.id

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /give {user} {amount}")
        return

    identifier = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом.")
        return

    target_user = get_user_by_identifier(chat_id, identifier)
    if not target_user:
        await update.message.reply_text("Пользователь не найден.")
        return

    to_user = target_user["user_id"]

    if from_user == to_user:
        await update.message.reply_text("Нельзя передать ремшекели самому себе.")
        return

    if not has_balance(chat_id, from_user, amount):
        await update.message.reply_text("У вас недостаточно ремшекелей.")
        return

    subtract_balance(chat_id, from_user, amount)
    add_balance(chat_id, to_user, amount)

    await update.message.reply_text(
        f"Вы передали <b>{amount} Ɍ</b> пользователю {escape(display_name(chat_id, to_user))}.",
        parse_mode="HTML"
    )


@requires_registration
async def drop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /drop {amount}")
        return

    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом.")
        return

    if not has_balance(chat_id, user_id, amount):
        await update.message.reply_text("У вас недостаточно ремшекелей.")
        return

    subtract_balance(chat_id, user_id, amount)
    await update.message.reply_text(f"Вы выбросили <b>{amount} Ɍ</b>.", parse_mode="HTML")


@requires_creator
async def grant_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /grant {user} {amount}")
        return

    identifier = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Сумма должна быть числом.")
        return

    target_user = get_user_by_identifier(chat_id, identifier)
    if not target_user:
        await update.message.reply_text("Пользователь не найден.")
        return

    to_user = target_user["user_id"]
    add_balance(chat_id, to_user, amount)

    await update.message.reply_text(
        f"Вы выдали <b>{amount} Ɍ</b> пользователю {escape(display_name(chat_id, to_user))}.",
        parse_mode="HTML"
    )
    
    
def get_wallet_handlers():
    handlers = [
        CommandHandler("balance", balance_handler),
        CommandHandler("give", give_handler),
        CommandHandler("drop", drop_handler),
        CommandHandler("grant", grant_handler)
    ]
    return handlers
