import os
from telegram import Update
from telegram.ext import ContextTypes
from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from spl.token.instructions import transfer_checked, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID

import base58
from dotenv import load_dotenv

load_dotenv()

wallets = {}

# Twój token
TOKEN_MINT = "BuLL65dUKeRgZ1TUo3g9F3SAgJmdwq23mcx7erb9QX9D"
DECIMALS = 9
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

# Secret key z Render
PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")
SENDER = Keypair.from_base58_string(PRIVATE_KEY)

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1 or not args[0].startswith("Bu"):
        await update.message.reply_text("❌ Podaj poprawny adres portfela Solana.")
        return
    wallets[update.effective_user.id] = args[0]
    await update.message.reply_text(f"🔗 Portfel zapisany: {args[0]}")

async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from solders.pubkey import Pubkey
    user = update.effective_user.id
    wallet = wallets.get(user)
    if not wallet:
        await update.message.reply_text("⚠️ Brak ustawionego portfela.")
        return

    async with AsyncClient(SOLANA_RPC) as client:
        ata = get_associated_token_address(Pubkey.from_string(wallet), Pubkey.from_string(TOKEN_MINT))
        result = await client.get_token_account_balance(ata)
        try:
            bal = result.value.ui_amount
            await update.message.reply_text(f"💼 Saldo: {bal:.2f} BULL")
        except:
            await update.message.reply_text("❌ Nie znaleziono tokenów w portfelu.")

async def send_tokens(destination: str, amount: float):
    from solders.pubkey import Pubkey

    dest_pubkey = Pubkey.from_string(destination)
    mint_pubkey = Pubkey.from_string(TOKEN_MINT)
    sender_ata = get_associated_token_address(SENDER.public_key, mint_pubkey)
    dest_ata = get_associated_token_address(dest_pubkey, mint_pubkey)

    async with AsyncClient(SOLANA_RPC) as client:
        tx = Transaction()
        tx.add(transfer_checked(
            sender=sender_ata,
            mint=mint_pubkey,
            dest=dest_ata,
            owner=SENDER.public_key,
            amount=int(amount * 10**DECIMALS),
            decimals=DECIMALS
        ))
        await client.send_transaction(tx, SENDER)

