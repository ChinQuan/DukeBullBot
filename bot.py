from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, price, spin, lottery
from handlers.spin import spin_button
import logging
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(CommandHandler("info", price.info))
    application.add_handler(CommandHandler("price", price.check_price))
    application.add_handler(CommandHandler("set_wallet", start.set_wallet))
    application.add_handler(CommandHandler("add_to_lottery", lottery.add_to_lottery))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start.echo))
    application.add_handler(CallbackQueryHandler(start.button))
    application.add_handler(CallbackQueryHandler(spin_button, pattern="^(double|take)$"))

    threading.Thread(target=lambda: time.sleep(60), daemon=True).start()
    application.run_polling(allowed_updates=None)

if __name__ == '__main__':
    main()
