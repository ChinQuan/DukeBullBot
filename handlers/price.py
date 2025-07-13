from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
import logging

logger = logging.getLogger(__name__)

PAIR_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n"

async def _fetch_json():
    async with aiohttp.ClientSession() as session:
        async with session.get(PAIR_URL) as resp:
            resp.raise_for_status()
            return await resp.json()

async def check_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await _fetch_json()
        pair = data["pairs"][0] if "pairs" in data else data["pair"]

        price_usd = float(pair["priceUsd"])
        fdv = float(pair.get("fdv", 0))
        volume = float(pair.get("volume", {}).get("h24", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        price_change = pair.get("priceChange", {}).get("h24", 0)

        message = (
            f"<b>Duke Bull [$BULL]</b>\n"
            f"💰 Cena: <b>${price_usd:.6f}</b>\n"
            f"📈 24h zmiana: <b>{price_change:.2f}%</b>\n"
            f"💧 Płynność: <b>${liquidity:,.0f}</b>\n"
            f"📊 FDV: <b>${fdv:,.0f}</b>\n"
            f"📉 Wolumen 24h: <b>${volume:,.0f}</b>\n"
            f"\n<a href='https://dexscreener.com/solana/{pair['pairAddress']}'>Dexscreener</a>"
        )
        await update.effective_message.reply_text(message, parse_mode="HTML")

    except Exception as e:
        logger.error(f"DexScreener request failed: {e}")
        await update.effective_message.reply_text("❌ Nie udało się pobrać ceny. Spróbuj ponownie później.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "ℹ️ Token Duke Bull ($BULL) to projekt memecoin na Solanie.\n\n"
        "💱 Cena i wykres: https://dexscreener.com/solana/gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n\n"
        "🌐 Strona: https://duke.bull\n"
        "🔗 Twitter: https://twitter.com/duketoken\n"
        "👥 Telegram: https://t.me/duketoken"
    )
