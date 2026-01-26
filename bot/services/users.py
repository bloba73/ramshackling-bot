from datetime import datetime
from storage.json_db import load_chat, save_chat
from config import START_BALANCE, MIN_NICK_LEN, MAX_NICK_LEN


def is_registered(chat_id: int, user_id: int) -> bool:
    chat = load_chat(chat_id)
    return str(user_id) in chat["users"]


def get_user(chat_id: int, user_id: int) -> dict | None:
    chat = load_chat(chat_id)
    return chat["users"].get(str(user_id))


def get_user_by_identifier(chat_id: int, identifier: str) -> dict | None:
    identifier = identifier.strip()
    chat = load_chat(chat_id)
    users = chat.get("users", {})

    try:
        uid = str(int(identifier))
        if uid in users:
            user = users[uid].copy()
            user["user_id"] = int(uid)
            return user
    except ValueError:
        pass

    identifier_lower = identifier.lower().lstrip("@")

    for uid, u in users.items():
        nickname = u.get("nickname")
        if nickname and nickname.lower() == identifier_lower:
            user = u.copy()
            user["user_id"] = int(uid)
            return user

    for uid, u in users.items():
        username = u.get("username")
        if username and username.lower().lstrip("@") == identifier_lower:
            user = u.copy()
            user["user_id"] = int(uid)
            return user

    return None


def display_name(chat_id: int, user_id: int) -> str:
    user = get_user(chat_id, user_id)
    if not user:
        return f"User {user_id}"
    return user.get("nickname") or user.get("username") or f"User {user_id}"


def register_user(chat_id: int, user_id: int, username: str | None, nickname: str | None) -> bool:
    chat = load_chat(chat_id)
    uid = str(user_id)

    if uid in chat["users"]:
        return False

    chat["users"][uid] = {
        "balance": START_BALANCE,
        "username": f"@{username}" if username else None,
        "nickname": nickname,
        "meta": {
            "created_at": datetime.utcnow().isoformat(),
            "last_action_at": None,
            "games_played": 0,
            "total_wins": 0,
            "total_losses": 0,
            "total_draws": 0,
            "max_amount_won": 0,
            "max_amount_lost": 0
        }
    }

    save_chat(chat_id, chat)
    return True


def set_nickname(chat_id: int, user_id: int, nickname: str) -> bool:
    chat = load_chat(chat_id)
    uid = str(user_id)
    user = chat["users"].get(uid)
    if not user:
        return False

    user["nickname"] = nickname.strip()
    chat["users"][uid] = user
    save_chat(chat_id, chat)
    return True


def validate_and_check_nickname(chat_id: int, nickname: str | None) -> str | None:
    if nickname is None:
        return None

    nickname = nickname.strip()

    if nickname.startswith("@"):
        return "Ник не может содержать символ @. Используйте имя без @ или '-' для пропуска."
    if nickname.startswith("/"):
        return "Ник не может начинаться с символа /. Используйте имя без / или '-' для пропуска."
    if not (MIN_NICK_LEN <= len(nickname) <= MAX_NICK_LEN):
        return f"Ник должен быть от {MIN_NICK_LEN} до {MAX_NICK_LEN} символов."

    chat = load_chat(chat_id)
    for user in chat.get("users", {}).values():
        if user.get("nickname") == nickname:
            return "Такой ник уже занят"
    
    return None


def touch_last_action(chat_id: int, user_id: int) -> bool:
    chat = load_chat(chat_id)
    user = chat["users"].get(str(user_id))
    if not user:
        return False

    user["meta"]["last_action_at"] = datetime.utcnow().isoformat()
    chat["users"][str(user_id)] = user
    save_chat(chat_id, chat)
    return True


def record_game_result(chat_id: int, user_id: int, won_amount: int) -> bool:
    chat = load_chat(chat_id)
    uid = str(user_id)
    user = chat["users"].get(uid)
    if not user:
        return False

    meta = user.get("meta", {})
    meta["games_played"] = meta.get("games_played", 0) + 1

    if won_amount > 0:
        meta["total_wins"] = meta.get("total_wins", 0) + 1
        meta["max_amount_won"] = max(meta.get("max_amount_won", 0), won_amount)
    elif won_amount < 0:
        meta["total_losses"] = meta.get("total_losses", 0) + 1
        meta["max_amount_lost"] = max(meta.get("max_amount_lost", 0), won_amount)
    else:
        meta["total_draws"] = meta.get("total_draws", 0) + 1

    user["meta"] = meta

    chat["users"][uid] = user
    save_chat(chat_id, chat)
    return True


def delete_user(chat_id: int, user_id: int) -> bool:
    chat = load_chat(chat_id)
    uid = str(user_id)

    if uid not in chat.get("users", {}):
        return False

    del chat["users"][uid]
    save_chat(chat_id, chat)
    return True
