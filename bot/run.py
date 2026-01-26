from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("Бот запущен")
    app.run_polling()
