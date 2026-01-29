import random
from telegram import Update
from telegram.ext import ContextTypes

class Dices:
    def __init__(self, chat_id: int, player1_id: int, player2_id: int, bet: int):
        self.chat_id = chat_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.bet = bet
        self.results = {}

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        roll1 = random.randint(1, 6)
        self.results[self.player1_id] = roll1
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"Игрок 1 бросает куб: {roll1}"
        )

        roll2 = random.randint(1, 6)
        self.results[self.player2_id] = roll2
        await context.bot.send_message(
            chat_id=self.chat_id,
            text=f"Игрок 2 бросает куб: {roll2}"
        )

        if roll1 > roll2:
            winner_text = f"Победил игрок 1! Ставка: {self.bet} Ɍ"
        elif roll2 > roll1:
            winner_text = f"Победил игрок 2! Ставка: {self.bet} Ɍ"
        else:
            winner_text = f"Ничья! Оба броска: {roll1}"

        await context.bot.send_message(chat_id=self.chat_id, text=winner_text)
