from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers.loader import load_handlers

def create_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    for handler in load_handlers():
        app.add_handler(handler)

    return app