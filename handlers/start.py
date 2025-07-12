from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

user_wallets = {}

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Sprawdź cenę", callback_data='price')],
        [InlineKeyboardButton("Informacje o tokenie", callback_data='info')],
        [InlineKeyboardButton("Zagraj w Spin", callback_data='spin')],
        [InlineKeyboardButton("Sprawdź Loterię", callback_data='lottery')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Witaj! Jestem botem dla tokena Duke Bull. Wybierz opcję:", reply_markup=get_main_menu())

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) != 1:
        await update.message.reply_text("Użyj: /set_wallet <adres_portfela>", reply_markup=get_main_menu())
        return
    wallet_address = args[0]
    if len(wallet_address) == 44 and wallet_address.startswith("5"):
        user_wallets[update.effective_user.id] = wallet_address
        await update.message.reply_text(f"Adres portfela {wallet_address} ustawiony!", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("Nieprawidłowy adres Solana!", reply_markup=get_main_menu())

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Wpisałeś: " + update.message.text, reply_markup=get_main_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    if data == 'price':
        from . import price
        await price.check_price(update, context)
    elif data == 'info':
        from . import price
        await price.info(update, context)
    elif data == 'spin':
        from . import spin
        await spin.spin_game(update, context)
    elif data == 'lottery':
        from . import lottery
        await lottery.check_lottery(update, context)
