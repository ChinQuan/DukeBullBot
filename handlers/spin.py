import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

games = {}
balances = {}

async def spin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bet = 0.1

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
