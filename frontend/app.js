const BACKEND_URL = "https://your-backend-url.com"; // Replace after deploy
const BULL_MINT = new solanaWeb3.PublicKey("BuLL65dUKeRgZ1TUo3g9F3SAgJmdwq23mcx7erb9QX9D");
const TREASURY = new solanaWeb3.PublicKey("FqzXYLitBn9oSb5tr3ffzJA4muxg47jSuiyjGUBNUXNz");
let provider = window.solana;
let connection = new solanaWeb3.Connection("https://api.mainnet-beta.solana.com");
let walletPublicKey = null;

async function connectWallet() {
  if (!provider?.isPhantom) {
    alert("Phantom wallet not found!");
    return;
  }
  const resp = await provider.connect();
  walletPublicKey = resp.publicKey;
  document.getElementById("wallet-address").innerText = "Connected: " + walletPublicKey.toBase58();
}

async function transferBULL(amount) {
  const token = await splToken.getOrCreateAssociatedTokenAccount(connection, provider, BULL_MINT, walletPublicKey);
  const treasuryToken = await splToken.getOrCreateAssociatedTokenAccount(connection, provider, BULL_MINT, TREASURY);
  const tx = new solanaWeb3.Transaction().add(
    splToken.createTransferInstruction(
      token.address,
      treasuryToken.address,
      walletPublicKey,
      amount,
      [],
      splToken.TOKEN_PROGRAM_ID
    )
  );
  const sig = await provider.signAndSendTransaction(tx);
  await connection.confirmTransaction(sig.signature);
  return sig.signature;
}

document.getElementById("connect-button").onclick = connectWallet;
document.getElementById("deposit-button").onclick = async () => {
  if (!walletPublicKey) return alert("Connect wallet first");
  await transferBULL(30000);
  alert("Deposited 30,000 BULL!");
};
document.getElementById("spin-button").onclick = async () => {
  if (!walletPublicKey) return alert("Connect wallet first");
  await transferBULL(1000);
  const win = Math.random() < 0.3;
  document.getElementById("result").innerText = win ? "🎉 You won! Sending 5,000 BULL..." : "❌ Try again!";
  if (win) {
    await fetch(BACKEND_URL + "/payout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ address: walletPublicKey.toBase58() })
    });
  }
};
