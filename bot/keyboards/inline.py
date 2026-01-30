from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def game_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Одиночная", callback_data=f"menu:single:open:{user_id}")
        ],
        [
            InlineKeyboardButton("Дуэльная", callback_data=f"menu:duel:open:{user_id}")
        ]
    ])

def solo_game_mode_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Coinflip", callback_data=f"menu:single:play:coinflip:{user_id}"),
            InlineKeyboardButton("Slot Machine", callback_data=f"menu:single:play:slotmachine:{user_id}"),
        ],
        [
            InlineKeyboardButton("Russian Roulette", callback_data=f"menu:single:play:roulette:{user_id}"),
            InlineKeyboardButton("Placeholder", callback_data=f"menu:single:play:p:{user_id}"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data=f"menu:root:open:{user_id}"),
        ]
    ])

def duel_game_mode_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Dices", callback_data=f"menu:duel:play:dices:{user_id}"),
            InlineKeyboardButton("Placeholder", callback_data=f"menu:duel:play:p:{user_id}"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data=f"menu:root:open:{user_id}"),
        ]
    ])

def duel_lobby_keyboard(owner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Присоединиться", callback_data=f"lobby:duel:join:{owner_id}")
            
        ],
        [
            InlineKeyboardButton("Отменить", callback_data=f"lobby:duel:cancel:{owner_id}")
        ]
    ])

def repeat_button(chat_id: int, user_id: int, bet: int, game_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Повторить ({bet})", callback_data=f"repeat:{game_name}:{bet}:{user_id}")
        ]
    ])