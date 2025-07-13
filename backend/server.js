// backend/server.js
// -----------------

// Core & middleware
const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
dotenv.config();

// Solana / SPL-Token
const {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  clusterApiUrl,
} = require("@solana/web3.js");
const {
  getOrCreateAssociatedTokenAccount,
  transfer,
  TOKEN_PROGRAM_ID,
} = require("@solana/spl-token");

// ─────────────────────────────────────────────
// App setup
// ─────────────────────────────────────────────
const app = express();
app.use(cors());            // ← CORS pozwala na wywołania z dowolnego originu
app.use(express.json());    // body-parser dla JSON

// ─────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────
const connection = new Connection("https://api.mainnet-beta.solana.com");

// PRIVATE_KEY w .env musi być 64-elementowym ciągiem liczb, np. 12,34,…
const secretKeyArr = process.env.PRIVATE_KEY.split(",").map(n => parseInt(n));
const payer        = Keypair.fromSecretKey(Uint8Array.from(secretKeyArr));

const BULL_MINT = new PublicKey(process.env.TOKEN_MINT);
const PAYOUT_AMOUNT = 5_000;        // ilość BULL do wypłaty

// ─────────────────────────────────────────────
// Endpoint: POST /payout
// ─────────────────────────────────────────────
app.post("/payout", async (req, res) => {
  try {
    const dest = new PublicKey(req.body.address);
    if (!dest) throw new Error("No destination address");

    // konta tokenowe
    const fromToken = await getOrCreateAssociatedTokenAccount(
      connection, payer, BULL_MINT, payer.publicKey
    );
    const toToken = await getOrCreateAssociatedTokenAccount(
      connection, payer, BULL_MINT, dest
    );

    // transfer SPL
    const sig = await transfer(
      connection,
      payer,                      // fee payer + signer
      fromToken.address,
      toToken.address,
      payer.publicKey,
      PAYOUT_AMOUNT,
      [],
      TOKEN_PROGRAM_ID
    );

    console.log(`[PAYOUT] Sent ${PAYOUT_AMOUNT} BULL to ${dest.toBase58()} → ${sig}`);
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
