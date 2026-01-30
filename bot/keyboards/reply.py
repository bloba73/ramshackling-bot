from telegram import ReplyKeyboardMarkup

def get_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["/help", "/gameinfo"],
            ["/registration", "/settings"],
            ["/leaderboard", "/balance"],
            ["/menu", "/settings"],
            ["/cancel", "/cancelgame"]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
