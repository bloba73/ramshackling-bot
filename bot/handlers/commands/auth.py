from html import escape
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.decorators import requires_registration
from services.users import delete_user, register_user, validate_and_check_nickname, display_name, is_registered
from services.states import States


async def registration_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if is_registered(chat_id, user.id):
        await update.message.reply_text("Вы уже зарегистрированы!")
        return ConversationHandler.END

    await update.message.reply_text(
        "Инициирована регистрация аккаунта.\n"
        "Введите свой никнейм, или отправьте '-' чтобы пропустить:"
    )
    return States.REGISTRATION_NICKNAME


async def registration_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    nickname = update.message.text.strip()

    if nickname == "-":
        nickname = None

    error = validate_and_check_nickname(chat_id, nickname)
    if error:
        await update.message.reply_text(error + "\nПопробуйте ещё раз:")
        return States.REGISTRATION_NICKNAME

    register_user(chat_id, user.id, user.username, nickname)
    name = escape(display_name(chat_id, user.id))
    await update.message.reply_text(
        f"Регистрация пользователя <b>{name}</b> завершена! Let's go gambling!",
        parse_mode="HTML"
    )
    return ConversationHandler.END


async def cancel_reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END


def get_registration_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("registration", registration_start)],
        states={
            States.REGISTRATION_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration_nickname)],
        },
        fallbacks=[CommandHandler("cancel", cancel_reg)],
        allow_reentry=True
    )


@requires_registration
async def delete_account_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вы собираетесь удалить свой аккаунт.\n"
        "Напишите 'да', чтобы подтвердить удаление.\n"
        "Или /cancel, чтобы отменить."
    )
    return States.DELETE_ACCOUNT_CONFIRM


async def delete_account_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_input.strip().lower() == "да":
        # Двойной I/O
        name = display_name(chat_id, user_id)
        success = delete_user(chat_id, user_id)
        if success:
            await update.message.reply_text(f"Аккаунт пользователя {name} успешно удалён.")
        else:
            await update.message.reply_text("Произошла ошибка при удалении аккаунта.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Удаление аккаунта отменено.")
        return ConversationHandler.END


async def cancel_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Удаление аккаунта отменено.")
    return ConversationHandler.END

    
def get_deleteaccount_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("deleteaccount", delete_account_start)],
        states={
            States.DELETE_ACCOUNT_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_account_confirm)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_del)],
        allow_reentry=True
    )