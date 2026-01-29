import random
from telegram import Update
from telegram.ext import ContextTypes

class Coinflip:
    def __init__(self, chat_id: int, user_id: int, bet: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.bet = bet

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = random.choice(["Орёл", "Решка"])
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"Ваша ставка: {self.bet} Ɍ\nРезультат: {result}"
        )
