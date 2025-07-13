
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from handlers.price import check_price, info
from handlers.spin import spin_game
from handlers.lottery import check_lottery

# Funkcja do komendy /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    "👋 Witaj w Duke Bull Bot!\nUżyj przycisków poniżej, aby rozpocząć.",
    reply_markup=get_main_menu()
)

# Funkcja do przycisku callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'price':
        await check_price(update, context)
    elif query.data == 'info':
        await info(update, context)
    elif query.data == 'spin':
        await spin_game(update, context)
    elif query.data == 'lottery':
        await check_lottery(update, context)

# Funkcja /set_wallet (placeholder)
async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💼 Funkcja ustawiania portfela jeszcze nie jest gotowa.")

# Echo dla zwykłych wiadomości (fallback)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Nie rozumiem tej wiadomości. Skorzystaj z menu.")

# Przyciskowe menu inline
def get_main_menu():
    buttons = [
        [InlineKeyboardButton("📈 Cena", callback_data='price')],
        [InlineKeyboardButton("ℹ️ Info", callback_data='info')],
        [InlineKeyboardButton("🎰 Spin", callback_data='spin')],
        [InlineKeyboardButton("🎟️ Loteria", callback_data='lottery')],
    ]
    return InlineKeyboardMarkup(buttons)
