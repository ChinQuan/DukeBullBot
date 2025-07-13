// backend/server.js
// -----------------

const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
dotenv.config();

const {
  Connection,
  Keypair,
  PublicKey,
  clusterApiUrl,
  sendAndConfirmTransaction,
  Transaction,
} = require("@solana/web3.js");

const {
  getOrCreateAssociatedTokenAccount,
  createTransferInstruction,
  TOKEN_PROGRAM_ID,
} = require("@solana/spl-token");

// ─────────────────────────────────────────────
// App setup
// ─────────────────────────────────────────────
const app = express();
app.use(cors());
app.use(express.json());

// ─────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────
const connection = new Connection("https://api.mainnet-beta.solana.com");

const secretKeyArr = process.env.PRIVATE_KEY.split(",").map(n => parseInt(n));
const payer = Keypair.fromSecretKey(Uint8Array.from(secretKeyArr));

const BULL_MINT = new PublicKey(process.env.TOKEN_MINT);
const PAYOUT_AMOUNT = 5000 * 10 ** 6; // zakładamy 6 miejsc po przecinku

// ─────────────────────────────────────────────
// Endpoint: POST /payout
// ─────────────────────────────────────────────
app.post("/payout", async (req, res) => {
  try {
    const dest = new PublicKey(req.body.address);
    if (!dest) throw new Error("No destination address");

    // znajdź lub utwórz token accounty
    const fromToken = await getOrCreateAssociatedTokenAccount(
      connection, payer, BULL_MINT, payer.publicKey
    );
    const toToken = await getOrCreateAssociatedTokenAccount(
      connection, payer, BULL_MINT, dest
    );

    // buduj transakcję
    const tx = new Transaction().add(
      createTransferInstruction(
        fromToken.address,
        toToken.address,
        payer.publicKey,
        PAYOUT_AMOUNT,
        [],
        TOKEN_PROGRAM_ID
      )
    );

    const sig = await sendAndConfirmTransaction(connection, tx, [payer]);

    console.log(`[PAYOUT] ✅ Sent 5000 BULL → ${dest.toBase58()} | ${sig}`);
    return res.json({ success: true, signature: sig });
  } catch (e) {
    console.error("[PAYOUT ERROR]", e);
    return res.status(500).json({ success: false, error: e.toString() });
  }
});

// ─────────────────────────────────────────────
// Start server
// ─────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});

