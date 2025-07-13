from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import handlers.price as price
from handlers.spin import spin_game
from handlers.lottery import check_lottery

def get_main_menu():
    buttons = [
        [InlineKeyboardButton("📈 Cena", callback_data="price")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("🎰 Spin", callback_data="spin")],
        [InlineKeyboardButton("🎟️ Loteria", callback_data="lottery")],
    ]
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "👋 Witaj w Duke Bull Bot!\nUżyj przycisków poniżej, aby rozpocząć.",
        reply_markup=get_main_menu(),
    )

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1 or not args[0].startswith("Bu"):
        await update.message.reply_text("Podaj poprawny adres portfela Solana. Przykład: /set_wallet BuXXXX")
        return
    from handlers.wallet import wallets
    wallets[update.effective_user.id] = args[0]
    await update.message.reply_text(f"🔗 Portfel ustawiony: {args[0]}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Nie rozumiem. Skorzystaj z menu poniżej.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "price":
        await price.check_price(update, context)
    elif query.data == "info":
        await price.info(update, context)
    elif query.data == "spin":
        await spin_game(update, context)
    elif query.data == "lottery":
        await check_lottery(update, context)
