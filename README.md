# KasiCred

Blockchain-based trust and credit ledger for informal street vendors in South Africa.

**Live:** [Vendor Dashboard](https://kasicred.onrender.com/) · [API Docs / WhatsApp Sim](https://kasicred-28bu.onrender.com/docs#/) · [Smart Contract (Celo Sepolia)](https://celo-sepolia.blockscout.com/address/0x40f805866f5923b376B5c722767cF17DD5f9d9Cb)

**Docs:** [Applied Research Paper](https://1drv.ms/w/c/0397c8827ea1fcf6/IQC9qscN-BwbTJKVbFHKfeHgAXHatVfmi5VQzFqkIxABUuQ) · [Customer Field Report](https://onedrive.live.com/:w:/g/personal/0397C8827EA1FCF6/IQCmfMYTUDMkS5vOW2h2GcOXAQebcQJ2_8vvu-Snmmrx2c4?resid=0397C8827EA1FCF6!s13c67ca633504b249bce5b687619c397&ithint=file%2Cdocx&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3cvYy8wMzk3Yzg4MjdlYTFmY2Y2L0lRQ21mTVlUVURNa1M1dk9XMmgyR2NPWEFRZWJjUUoyXzh2dnUtU25tbXJ4MmM0) · [Vendor Field Report](https://onedrive.live.com/:w:/g/personal/0397C8827EA1FCF6/IQBJchfUPDabR6bD3GfedfvtAYbxcx44V-FlhR64qLl0RZA?resid=0397C8827EA1FCF6!sd4177249363c479ba6c3dc67de75fbed&ithint=file%2Cdocx&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3cvYy8wMzk3Yzg4MjdlYTFmY2Y2L0lRQkpjaGZVUERhYlI2YkQzR2ZlZGZ2dEFZYnhjeDQ0Vi1GbGhSNjRxTGwwUlpB)

## The Problem

South Africa's informal sector contributes an estimated 23.7% of GDP, yet most
vendors — roughly 60% classified as cash-only "survivalist" businesses — remain
invisible to formal financial systems. No transaction history, no credit trail,
no way to prove they're worth lending to.

## What KasiCred Does

- A vendor registers via phone number and receives a QR code. A buyer scans it
  after a purchase and submits a star rating — no app download required.
- Each rating is hashed (SHA-256) and stored on the Celo blockchain for
  tamper-proof integrity. Review content (text, issue category) stays in
  SQLite to keep gas costs low.
- The backend relayer is the only address permitted to write to the contract —
  buyers and vendors never interact with the chain directly.
- Vendors see a **trust score (0–100)** derived from their on-chain average,
  with a **Loan Ready** badge at 80+. This is the number a microlender sees.
- Over time, a vendor builds a portable, exportable proof-of-business record —
  something they can show a lender that doesn't exist today.

## Repo Structure

```
├── frontend/              # Static site (React prototype, deployed to Render)
│   ├── index.html
│   └── kasicred_vendor.jsx
├── backend/               # FastAPI relayer + SQLite persistence
│   ├── app.py             # API endpoints: register, vendor lookup, review
│   ├── celo_client.py     # Web3 connection, contract calls, tx signing
│   └── db.py              # SQLite schema, queries (vendors + reviews)
├── contracts/
│   └── KasiCredTrustLedger.sol   # Solidity contract (Celo testnet)
├── Procfile               # uvicorn backend.app:app
└── requirements.txt       # Python dependencies
```

## How It Works

1. **Vendor registers** — `POST /vendor/register` with name, phone, area,
   items sold. Phone number is deterministically hashed to a Celo address.
   Vendor row persists in SQLite.

2. **Buyer rates** — `POST /review/phone` with score (1–5) and review text.
   Backend hashes the review, calls `recordReview()` on-chain via the relayer,
   then writes the full review to SQLite.

3. **Dashboard** — `GET /vendor/phone/{id}` returns on-chain average score +
   review count, plus recent reviews from SQLite. Frontend converts the
   1–5 average to a 0–100 trust score and displays a Loan Ready / Building
   badge.

4. **WhatsApp flow** — A multi-step conversational path collects rating,
   optional comment, and low-rating feedback reason before committing to
   chain. Session state is in-memory (ephemeral).

## Trust Score

On-chain, scores are 1–5 integers. The contract returns `(averageScore * 10)`,
e.g. 46 = 4.6 average. The frontend maps this to 0–100:

- **80–100**: Loan Ready (green badge)
- **0–79**: Building (amber badge)

This is the single scoring system used across prototype screens, dashboard, and
all docs — there is no separate "742" or other unscaled number.

## Security

- **Contract access control**: `recordReview()` is gated by an `onlyRelayer`
  modifier. Only the backend's private key can write reviews. Anyone calling
  the contract directly gets `require` failed.
- **Relayer rotation**: `transferRelayer(address)` lets you rotate the signing
  key without redeploying.
- **No GPS stored**: only a vendor-entered market/area name.
- **Review hashing**: review text is SHA-256 hashed on-chain; the full text
  lives only in SQLite, disclosed only to parties the vendor chooses.

**Note**: The currently deployed contract on Celo testnet predates the
`onlyRelayer` fix. It must be redeployed and `CONTRACT_ADDRESS` updated in
the backend environment.

## Tech Stack (actually in use)

| Layer | Tech |
|---|---|
| Frontend | React 18 (UMD), Babel standalone, inline styles |
| Backend | FastAPI, uvicorn, Web3.py |
| Database | SQLite (vendors + reviews, foreign keys, indexed) |
| Blockchain | Celo testnet, Solidity 0.8.20 |
| Deployment | Render (static frontend + Python web service) |

## Local Development

1. **Clone and install:**
   ```bash
   git clone https://github.com/nyaks1/KasiCred.git
   cd KasiCred
   pip install -r requirements.txt
   ```

2. **Configure environment** (`.env` in repo root):
   ```
   CELO_RPC_URL=https://forno.celo-sepolia.celo-testnet.org
   RELAYER_PRIVATE_KEY=your_private_key_here
   CONTRACT_ADDRESS=your_deployed_contract_address
   KASICRED_DB_PATH=kasicred.db
   ```

3. **Run the backend:**
   ```bash
   uvicorn backend.app:app --reload
   ```

4. **Run the frontend** (any static server):
   ```bash
   python3 -m http.server 8763 --directory frontend
   ```
   Open `http://localhost:8763`. Set `window.KASICRED_API_URL = "http://localhost:8000"` in the browser console to point at your local backend.

## What's Not Built Yet

- **Rating weighting** — scores are passed through raw (1–5). Transaction-size
  weighting and buyer repeat-purchase history are designed but not implemented.
- **WhatsApp Business API** — the conversational flow exists as an in-memory
  state machine, not connected to a real WhatsApp number.
- **QR code generation** — signup returns a URI string, not a printable QR.
- **Vulavula / Gemma** — multilingual creditworthiness summarisation is
  planned, not built.
- **Proof-of-business PDF export** — button exists, download does not.

## Privacy & POPIA

- No GPS captured — only a vendor-entered market/area name.
- Ledger data is disclosed only to parties the vendor explicitly chooses.
- Raw voice input (where used) is discarded after transcription.
- Hosted africa-south1 where cloud infrastructure is used.

## Team

Nyakallo · Khatisani · Liya — WeThinkCode_
