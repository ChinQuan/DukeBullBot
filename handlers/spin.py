import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from handlers.wallet import wallets, send_tokens

SPIN_COST = 1000  # koszt w BULL
WIN_CHANCE = 0.25
DECIMALS = 9

winnings = {}  # tymczasowy storage dla wygranych

async def spin_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    wallet_address = wallets.get(user_id)

    if not wallet_address:
        await update.effective_message.reply_text("❌ Nie masz ustawionego portfela. Użyj /set_wallet <adres>")
        return

    # odejmij SPIN_COST z konta (jeśli implementujesz to on-chain, tu będzie kod)
    if random.random() <= WIN_CHANCE:
        amount = round(random.uniform(1.1, 3.0), 2)
        winnings[user_id] = amount
        buttons = [
            [InlineKeyboardButton("🎲 DOUBLE", callback_data="double")],
            [InlineKeyboardButton("💰 TAKE", callback_data="take")]
        ]
        await update.effective_message.reply_text(
            f"🎉 Trafiłeś {amount:.2f}!\nChcesz spróbować podwoić?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await update.effective_message.reply_text("😢 Nic nie wygrałeś. Spróbuj ponownie!")

async def spin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    wallet_address = wallets.get(user_id)

    if not wallet_address:
        await query.edit_message_text("❌ Portfel nie ustawiony.")
        return

    last_win = winnings.get(user_id)
    if not last_win:
        await query.edit_message_text("❌ Brak ostatniej wygranej.")
        return

    if query.data == "double":
        if random.random() <= 0.5:
            winnings[user_id] *= 2
            buttons = [
                [InlineKeyboardButton("🎲 DOUBLE", callback_data="double")],
                [InlineKeyboardButton("💰 TAKE", callback_data="take")]
            ]
            await query.edit_message_text(
                f"🔥 Udało się! Masz teraz {winnings[user_id]:.2f}!\nGrasz dalej?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            del winnings[user_id]
            await query.edit_message_text("❌ Przegrałeś wszystko!")
    elif query.data == "take":
        amount = winnings.pop(user_id)
        await query.edit_message_text(f"✅ Wypłacam {amount:.2f} BULL do Twojego portfela.")
        await send_tokens(wallet_address, amount)
