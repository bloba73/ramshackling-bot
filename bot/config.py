import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
START_BALANCE = int(os.getenv("START_BALANCE", 0))
MIN_NICK_LEN = int(os.getenv("MIN_NICK_LEN", 1))
MAX_NICK_LEN = int(os.getenv("MAX_NICK_LEN", 25))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")
