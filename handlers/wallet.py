# handlers/wallet.py

from telegram import Update
from telegram.ext import ContextTypes

wallets = {}  # user_id -> wallet_address

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1 or not args[0].startswith("Bu"):
        await update.message.reply_text("Podaj poprawny adres portfela Solana. Przykład: /link BuXXXX")
        return

    wallets[update.effective_user.id] = args[0]
    await update.message.reply_text(f"🔗 Portfel ustawiony: {args[0]}")

async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from handlers.spin import balances
    bal = balances.get(user_id, 0)
    addr = wallets.get(user_id, "Nie ustawiony")
    await update.message.reply_text(f"👛 Portfel: {addr}\n💰 Saldo: {bal:.2f} BULL")
