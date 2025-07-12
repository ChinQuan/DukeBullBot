# handlers/price.py
import os
import logging
import asyncio
from datetime import timedelta

import aiohttp
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.start import get_main_menu, alerts  # ← istniejące słowniki/menu

logger = logging.getLogger(__name__)

# === Konfiguracja z ENV ======================================================
BULL_TOKEN_ADDRESS = os.getenv("BULL_TOKEN_ADDRESS", "").strip()
if not BULL_TOKEN_ADDRESS:
    raise RuntimeError("Brak zmiennej BULL_TOKEN_ADDRESS w środowisku!")

DEX_PAIR_URL = (
    f"https://api.dexscreener.com/latest/dex/pairs/solana/{BULL_TOKEN_ADDRESS}"
)
BIRDEYE_API = f"https://public-api.birdeye.so/public/token/{BULL_TOKEN_ADDRESS}"
DEX_LINK = f"https://dexscreener.com/solana/{BULL_TOKEN_ADDRESS}"
BIRDEYE_LINK = f"https://birdeye.so/token/{BULL_TOKEN_ADDRESS}?chain=solana"

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "demo")  # demo → 10 req/min
# ============================================================================


# ---------- funkcje pomocnicze ----------------------------------------------
async def _fetch_json(session: aiohttp.ClientSession, url: str, **kwargs):
    try:
        async with session.get(url, timeout=10, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()
    except Exception as exc:
        logger.exception("Błąd przy pobieraniu %s: %s", url, exc)
        return None


def _format_number(value: float, prec: int = 2) -> str:
    """Formatuje liczby 12_300 → 12.3K itp."""
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.{prec}f}B"
    if value >= 1_000_000:
        return f"{value/1_000_000:.{prec}f}M"
    if value >= 1_000:
        return f"{value/1_000:.{prec}f}K"
    return f"{value:.{prec}f}"


def _age_to_human(seconds: int) -> str:
    td = timedelta(seconds=seconds)
    days = td.days
    weeks, days = divmod(days, 7)
    parts = []
    if weeks:
        parts.append(f"{weeks}w")
    if days:
        parts.append(f"{days}d")
    return " ".join(parts) or "—"
# -----------------------------------------------------------------------------


async def check_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Główny handler wywoływany przy /price lub przycisku 'Price'."""
    async with aiohttp.ClientSession(
        headers={"x-api-key": BIRDEYE_API_KEY}
    ) as session:
        # równolegle pobieramy oba API
        dexscreener_task = asyncio.create_task(_fetch_json(session, DEX_PAIR_URL))
        birdeye_task = asyncio.create_task(_fetch_json(session, BIRDEYE_API))

        dexscreener_data = await dexscreener_task
        birdeye_data = await birdeye_task

    if not dexscreener_data:
        await update.effective_message.reply_text(
            "⚠️ Nie udało się pobrać danych z DexScreener. Spróbuj ponownie później."
        )
        return

    pair = dexscreener_data.get("pair", {})
    price_usd = float(pair.get("priceUsd", 0))
    fdv = float(pair.get("fdv", 0))
    liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0))
    volume_24h = float(pair.get("volume", {}).get("h24", 0))
    ath = float(pair.get("ath", {}).get("price", 0))
    change_1h = float(pair.get("priceChange", {}).get("h1", 0))
    age_seconds = int(pair.get("age", 0))

    # z Birdeye (opcjonalnie)
    holders = birdeye_data.get("data", {}).get("holders", "—") if birdeye_data else "—"
    fresh_1d = birdeye_data.get("data", {}).get("freshWallets1d", "—") if birdeye_data else "—"
    fresh_7d = birdeye_data.get("data", {}).get("freshWallets7d", "—") if birdeye_data else "—"

    # ---------- budujemy wiadomość ------------------------------------------
    message = (
        f"🚀 *Duke Bull* [$BULL]\\n"
        f"🏦 Solana @ Raydium Cpmm\\n"
        f"💲 *USD:* `${price_usd:.8f}`\\n"
        f"💰 *FDV:* ${_format_number(fdv)} ↔ *ATH:* ${_format_number(ath)} *(now!)*\\n"
        f"🔒 *Liq:* ${_format_number(liquidity_usd)} | *LP:* 0% ‼️\\n"
        f"📊 *Vol:* ${_format_number(volume_24h)} • *Age:* {_age_to_human(age_seconds)}\\n"
        f"📈 *1H:* {change_1h:.1f}%\\n"
        f"🤝 *Holders:* {holders}\\n"
        f"🌱 *Fresh 1D:* {fresh_1d}% • *7D:* {fresh_7d}%\\n

