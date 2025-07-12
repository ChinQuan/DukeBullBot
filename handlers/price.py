import requests
from telegram import Update
from telegram.ext import ContextTypes
from handlers.start import get_main_menu, alerts
import os
import logging

# Stałe
DEX_PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n"
BIRDEYE_TOKEN_ADDRESS = "BuLL65dUKeRgZ1TUo3g9F3SAgJmdwq23mcx7erb9QX9D"
BIRDEYE_API = f"https://public-api.birdeye.so/public/token/{BIRDEYE_TOKEN_ADDRESS}"
BIRDEYE_LINK = f"https://birdeye.so/token/{BIRDEYE_TOKEN_ADDRESS}?chain=solana"
DEX_LINK = "https://dexscreener.com/solana/gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n"

logger = logging.getLogger(__name__)

async def check_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Pobieramy dane z Dexscreener
        dexscreener_data = requests.get(DEX_PAIR_URL, timeout=10).json()
        pair = dexscreener_data.get("pair", {})
        price_usd = float(pair.get("priceUsd", 0))
        fdv = float(pair.get("fdv", 0))
        liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0))
        volume_24h = float(pair.get("volume", {}).get("h24", 0))
        ath = float(pair.get("ath", {}).get("price", 0))
        age = pair.get("age", "N/A")
        change_1h = float(pair.get("priceChange", {}).get("h1", 0))

        # Pobieramy dodatkowe dane z Birdeye (np. holders, fresh wallets) - opcjonalnie
        headers = {"X-API-KEY": "demo"}  # jeśli masz klucz, podmień
        birdeye_data = requests.get(BIRDEYE_API, headers=headers, timeout=10).json()
        holders = birdeye_data.get("data", {}).get("holders", "N/A")

        message = (
            "💥 *Duke Bull* [$BULL]\n"
            f"💵 USD: `${price_usd:.8f}`\n"
            f"📈 ATH: `${ath:.6f}`\n"
            f"💰 FDV: `${fdv:,.0f}`\n"
            f"💧 Liq: `${liquidity_usd:,.0f}`\n"
            f"📊 Vol 24h: `${volume_24h:,.0f}`\n"
            f"⏳ Age: {age}\n"
            f"📉 1H: {change_1h:.2f}%\n"
            f"👥 Holders: {holders}\n\n"
            f"[Dex Screener]({DEX_LINK}) | [Birdeye]({BIRDEYE_LINK})"
        )
        await update.callback_query.edit_message_text(message, reply_markup=get_main_menu(), parse_mode="Markdown")

        # Alerty cenowe
        user_id = update.effective_user.id
        if user_id in alerts and price_usd >= alerts[user_id]:
            await context.bot.send_message(chat_id=user_id, text=f"🚨 Cena przekroczyła ustawiony alert: ${price_usd:.8f}")
            del alerts[user_id]
    except Exception as e:
        logger.error(f"Price error: {e}")
        await update.callback_query.edit_message_text(f"Błąd pobierania danych: {e}", reply_markup=get_main_menu())

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_price(update, context)

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) != 1:
        await update.message.reply_text("Użyj: /set_alert <cena>")
        return
    try:
        price = float(args[0])
        alerts[update.effective_user.id] = price
        await update.message.reply_text(f"🔔 Alert ustawiony na ${price:.8f}")
    except ValueError:
        await update.message.reply_text("Podaj prawidłową liczbę")
