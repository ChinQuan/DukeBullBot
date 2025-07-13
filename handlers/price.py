# handlers/start.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import handlers.price as price
from handlers.spin import spin_game
from handlers.lottery import check_lottery

# === Funkcja menu głównego ==================================================

def get_main_menu():
    buttons = [
        [InlineKeyboardButton("📈 Cena", callback_data="price")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("🎰 Spin", callback_data="spin")],
        [InlineKeyboardButton("🎟️ Loteria", callback_data="lottery")],
    ]
    return InlineKeyboardMarkup(buttons)

# === Handlery komend /start, /set_wallet, echo ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        """👋 Witaj w Duke Bull Bot!
Użyj przycisków poniżej, aby rozpocząć.""",
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

# === Obsługa przycisków inline ==============================================

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


# ---------------------------------------------------------------------------
# Poniżej pozostaje wcześniej zapisany plik spin.py bez zmian
# handlers/spin.py
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Przechowujemy stan gry oraz balans użytkownika (tymczasowo w RAMie)
games = {}  # user_id -> dict(state, amount)
balances = {}  # user_id -> float

async def spin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bet = 0.1  # domyślna stawka w tokenie/SOL

    roll = random.randint(1, 100)
    if roll <= 55:
        await update.effective_message.reply_text("🎯 Miss! Przegrałeś.")
        return
    elif roll <= 90:
        win = bet
    else:
        win = bet * 2

    games[user_id] = {"state": "double", "amount": win}
    await update.effective_message.reply_text(
        f"🎉 Trafiłeś {win:.2f}!\nChcesz spróbować podwoić?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 DOUBLE", callback_data="double")],
            [InlineKeyboardButton("💰 TAKE", callback_data="take")],
        ])
    )

async def spin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    game = games.get(user_id)

    if not game:
        await query.answer("Brak aktywnej gry.")
        return

    if query.data == "take":
        balances[user_id] = balances.get(user_id, 0) + game["amount"]
        del games[user_id]
        await query.edit_message_text(f"💰 Zgarnąłeś {game['amount']:.2f} – gratki!")

    elif query.data == "double":
        color = random.choice(["red", "black"])
        if random.random() < 0.48:
            game["amount"] *= 2
            await query.edit_message_text(
                f"❤️ {color.capitalize()}! Wygrana {game['amount']:.2f}.\nChcesz spróbować jeszcze raz?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎲 DOUBLE", callback_data="double")],
                    [InlineKeyboardButton("💰 TAKE", callback_data="take")],
                ])
            )
        else:
            del games[user_id]
            await query.edit_message_text("🖤 Pudło! Straciłeś wszystko 😢")

# Dodajemy brakującą funkcję info do handlers/price.py
# handlers/price.py
from telegram import Update
from telegram.ext import ContextTypes

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "ℹ️ Token Duke Bull ($BULL) to projekt memecoin na Solanie.\n\n"
        "💱 Cena i wykres: https://dexscreener.com/solana/gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n\n"
        "🌐 Strona: https://duke.bull\n"
        "🔗 Twitter: https://twitter.com/duketoken\n"
        "👥 Telegram: https://t.me/duketoken"
    )
