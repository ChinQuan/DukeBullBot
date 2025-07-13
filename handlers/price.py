# handlers/price.py
import logging
import asyncio
from datetime import timedelta

import aiohttp
from telegram import Update, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# ==== Lokalna wersja menu i alertów (obejście circular import) ==============
alerts = {}

def get_main_menu():
    return InlineKeyboardMarkup([])  # ← tu możesz dodać własne przyciski
# ============================================================================

PAIR_ADDRESS = "gae6rs1n2xz5yywppf2pepub1krzpqh8sw43dzmnge7n"
DEX_API_URL = f"https://api.dexscreener.com/latest/dex/pairs/solana/{PAIR_ADDRESS}"
DEX_LINK = f"https://dexscreener.com/solana/{PAIR_ADDRESS}"

logger = logging.getLogger(__name__)

async def _fetch_json(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            return await resp.json()
    except Exception as exc:
        logger.exception("DexScreener request failed: %s", exc)
        return None

def _human_n(num: float, prec: int = 2) -> str:
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.{prec}f}B"
    if num >= 1_000_000:
        return f"{num/1_000_000:.{prec}f}M"
    if num >= 1_000:
        return f"{num/1_000:.{prec}f}K"
    return f"{num:.{prec}f}"

def _age_to_human(seconds: int) -> str:
    td = timedelta(seconds=seconds)
    weeks, days = divmod(td.days, 7)
    out = []
    if weeks:
        out.append(f"{weeks}w")
    if days:
        out.append(f"{days}d")
    return " ".join(out) or "—"

async def check_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as session:
        data = await _fetch_json(session, DEX_API_URL)

    if not data:
        await update.effective_message.reply_text(
            "⚠️ Nie udało się pobrać danych z DexScreener. Spróbuj ponownie później."
        )
        return

    pair = data.get("pair", {})
    price = float(pair.get("priceUsd", 0))
    fdv = float(pair.get("fdv", 0))
    liq = float(pair.get("liquidity", {}).get("usd", 0))
    vol24 = float(pair.get("volume", {}).get("h24", 0))
    ath = float(pair.get("ath", {}).get("price", 0))
    age = _age_to_human(int(pair.get("age", 0)))
    chg1h = float(pair.get("priceChange", {}).get("h1", 0))

    message = (
        f"🚀 *Duke Bull* [$BULL]\n"
        f"🏦 Solana @ Raydium Cpmm\n"
        f"💲 *USD:* `${price:.8f}`\n"
        f"💰 *FDV:* ${_human_n(fdv)} ↔ *ATH:* ${_human_n(ath)} *(now!)*\n"
        f"🔒 *Liq:* ${_human_n(liq)}\n"
        f"📊 *Vol:* ${_human_n(vol24)} • *Age:* {age}\n"
        f"📈 *1H:* {chg1h:.1f}%\n\n"
        f"[Chart]({DEX_LINK})"
    )

    await update.effective_message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
        reply_markup=get_main_menu(),
    )

    user_id = update.effective_user.id
    if (alert_price := alerts.get(user_id)) is not None and price <= alert_price:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🔔 Cena spadła do ${price:.8f}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        del alerts[user_id]

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_price(update, context)

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Użyj: /set_alert <cena>")
        return
    try:
        price = float(args[0])
        alerts[update.effective_user.id] = price
        await update.message.reply_text(f"🔔 Alert ustawiony na ${price:.8f}")
    except ValueError:
        await update.message.reply_text("Podaj prawidłową liczbę")
