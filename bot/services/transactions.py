from storage.json_db import load_chat, save_chat

def get_balance(chat_id: int, user_id: int) -> int:
    chat = load_chat(chat_id)
    user = chat["users"].get(str(user_id))
    return user.get("balance", 0) if user else 0


def has_balance(chat_id: int, user_id: int, amount: int) -> bool:
    return get_balance(chat_id, user_id) >= amount


def add_balance(chat_id: int, user_id: int, amount: int) -> bool:
    if amount <= 0:
        return False

    chat = load_chat(chat_id)
    uid = str(user_id)
    user = chat["users"].get(uid)
    if not user:
        return False

    user["balance"] = user.get("balance", 0) + amount
    chat["users"][uid] = user
    save_chat(chat_id, chat)
    return True


def subtract_balance(chat_id: int, user_id: int, amount: int) -> bool:
    if amount <= 0:
        return False

    chat = load_chat(chat_id)
    uid = str(user_id)
    user = chat["users"].get(uid)
    if not user or user.get("balance", 0) < amount:
        return False

    user["balance"] -= amount
    chat["users"][uid] = user
    save_chat(chat_id, chat)
    return True


def transfer(chat_id: int, from_user: int, to_user: int, amount: int) -> bool:
    if amount <= 0 or from_user == to_user:
        return False

    chat = load_chat(chat_id)
    uid_from = str(from_user)
    uid_to = str(to_user)

    sender = chat["users"].get(uid_from)
    receiver = chat["users"].get(uid_to)

    if not sender or not receiver or sender.get("balance", 0) < amount:
        return False

    sender["balance"] -= amount
    receiver["balance"] += amount

    chat["users"][uid_from] = sender
    chat["users"][uid_to] = receiver
    save_chat(chat_id, chat)
    return True
