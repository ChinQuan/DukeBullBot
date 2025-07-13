# handlers/wallet.py

import os
import base58
import logging
from dotenv import load_dotenv
from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.rpc.commitment import Confirmed
from spl.token.instructions import transfer_checked, get_associated_token_address
from spl.token.constants import TOKEN_PROGRAM_ID

from telegram import Update
from telegram.ext import ContextTypes

load_dotenv()
logger = logging.getLogger(__name__)

# Adres mint tokena $BULL
MINT_ADDRESS = "BuLL65dUKeRgZ1TUo3g9F3SAgJmdwq23mcx7erb9QX9D"
DECIMALS = 9

# Private key (w Base58) trzymany w zmiennej środowiskowej
PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")

# Inicjalizacja klucza nadawcy
private_key_bytes = base58.b58decode(PRIVATE_KEY)
SENDER = Keypair.from_secret_key(private_key_bytes)

wallets = {}  # user_id -> wallet address


# ===== Komenda do ustawiania portfela ===================================

async def set_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1 or not args[0].startswith("Bu"):
        await update.message.reply_text("❌ Podaj poprawny adres portfela Solana. Przykład: /set_wallet BuXXXX")
        return
    user_id = update.effective_user.id
    wallets[user_id] = args[0]
    await update.message.reply_text(f"✅ Portfel ustawiony: {args[0]}")


# ===== Komenda do sprawdzania balansu (opcjonalna) ======================

async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in wallets:
        await update.message.reply_text("❌ Najpierw ustaw swój portfel komendą /set_wallet")
        return

    user_wallet = wallets[user_id]
    ata = get_associated_token_address(pubkey=user_wallet, mint=MINT_ADDRESS)
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        resp = await client.get_token_account_balance(ata)
        if "value" in resp["result"]:
            amount = int(resp["result"]["value"]["amount"]) / (10 ** DECIMALS)
            await update.message.reply_text(f"💰 Saldo portfela: {amount:.2f} BULL")
        else:
            await update.message.reply_text("💼 Brak tokenów BULL na portfelu.")


# ===== Funkcja do przesyłania tokenów SPL ===============================

async def send_tokens(destination: str, amount: float) -> bool:
    try:
        async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
            from solana.publickey import PublicKey
            from spl.token.client import Token

            mint_pubkey = PublicKey(MINT_ADDRESS)
            sender_pubkey = SENDER.public_key
            destination_pubkey = PublicKey(destination)

            ata_sender = get_associated_token_address(sender_pubkey, mint_pubkey)
            ata_receiver = get_associated_token_address(destination_pubkey, mint_pubkey)

            tx = Transaction()
            tx.add(
                transfer_checked(
                    program_id=TOKEN_PROGRAM_ID,
                    source=ata_sender,
                    mint=mint_pubkey,
                    dest=ata_receiver,
                    owner=sender_pubkey,
                    amount=int(amount * (10 ** DECIMALS)),
                    decimals=DECIMALS
                )
            )

            result = await client.send_transaction(tx, SENDER)
            logger.info(f"💸 Wysłano {amount} BULL do {destination}: {result}")
            return True
    except Exception as e:
        logger.error(f"❌ Błąd podczas wysyłki tokenów: {e}")
        return False

