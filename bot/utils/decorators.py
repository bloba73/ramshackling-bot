from functools import wraps
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram import ChatMember, Update
from services.gamesessions import game_sessions
from services.users import is_registered


def requires_creator(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await is_creator(update):
            await update.message.reply_text("Только создатель группы может использовать эту команду.")
            return
        return await func(update, context)
    return wrapper


async def is_creator(update):
    user_id = update.effective_user.id
    chat = update.effective_chat

    member: ChatMember = await chat.get_member(user_id)
    return member.status == "creator"


def requires_registration(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat

        if not user or not chat:
            return

        if not is_registered(chat.id, user.id):
            await update.message.reply_text(
                "Ты не зарегистрирован."
            )
            return

        return await func(update, context)

    return wrapper


def handle_telegram_errors(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except BadRequest as e:
            if "Message is not modified" in str(e):
                return
            else:
                raise
    return wrapper


def requires_no_active_session(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        if game_sessions.has_active(chat_id, user_id):
            await update.effective_message.reply_text(
                "У вас уже есть активная игра."
            )
            return

        return await func(update, context)
    return wrapper
