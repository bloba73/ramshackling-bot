from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def game_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Одиночная", callback_data="menu:single:open"),
            InlineKeyboardButton("Дуэльная", callback_data="menu:duel:open"),
        ]
    ])

def solo_game_mode_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Placeholder", callback_data="menu:single:p1"),
            InlineKeyboardButton("Placeholder", callback_data="menu:single:p2"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="menu:root:open"),
        ]
    ])

def duel_game_mode_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Placeholder", callback_data="menu:duel:p1"),
            InlineKeyboardButton("Placeholder", callback_data="menu:duel:p2"),
        ],
        [
            InlineKeyboardButton("Назад", callback_data="menu:root:open"),
        ]
    ])
