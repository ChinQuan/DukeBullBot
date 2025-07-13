const express = require("express");
const { Connection, Keypair, PublicKey, clusterApiUrl, Transaction } = require("@solana/web3.js");
const { getOrCreateAssociatedTokenAccount, transfer, TOKEN_PROGRAM_ID } = require("@solana/spl-token");
require("dotenv").config();
const app = express();
app.use(express.json());

const connection = new Connection("https://api.mainnet-beta.solana.com");
const payer = Keypair.fromSecretKey(Uint8Array.from(process.env.PRIVATE_KEY.split(",").map(n => parseInt(n))));
const BULL_MINT = new PublicKey(process.env.TOKEN_MINT);

app.post("/payout", async (req, res) => {
  try {
    const dest = new PublicKey(req.body.address);
    const fromToken = await getOrCreateAssociatedTokenAccount(connection, payer, BULL_MINT, payer.publicKey);
    const toToken = await getOrCreateAssociatedTokenAccount(connection, payer, BULL_MINT, dest);
    const sig = await transfer(
      connection, payer, fromToken.address, toToken.address, payer, 5000, [], TOKEN_PROGRAM_ID
    );
    res.json({ success: true, signature: sig });
  } catch (e) {
    console.error(e);
    res.status(500).json({ success: false, error: e.toString() });
  }
});

app.listen(3000, () => console.log("Backend running on port 3000"));