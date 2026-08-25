# KasiCred

Blockchain-based trust and credit ledger for informal street vendors in South Africa.

Paper: [\[Applied Research and Working Paper](https://1drv.ms/w/c/0397c8827ea1fcf6/IQC9qscN-BwbTJKVbFHKfeHgAXHatVfmi5VQzFqkIxABUuQ)

[Customer Field Report](https://onedrive.live.com/:w:/g/personal/0397C8827EA1FCF6/IQCmfMYTUDMkS5vOW2h2GcOXAQebcQJ2_8vvu-Snmmrx2c4?resid=0397C8827EA1FCF6!s13c67ca633504b249bce5b687619c397&ithint=file%2Cdocx&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3cvYy8wMzk3Yzg4MjdlYTFmY2Y2L0lRQ21mTVlUVURNa1M1dk9XMmgyR2NPWEFRZWJjUUoyXzh2dnUtU25tbXJ4MmM0)

[Vendor Field Report](https://onedrive.live.com/:w:/g/personal/0397C8827EA1FCF6/IQBJchfUPDabR6bD3GfedfvtAYbxcx44V-FlhR64qLl0RZA?resid=0397C8827EA1FCF6!sd4177249363c479ba6c3dc67de75fbed&ithint=file%2Cdocx&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3cvYy8wMzk3Yzg4MjdlYTFmY2Y2L0lRQkpjaGZVUERhYlI2YkQzR2ZlZGZ2dEFZYnhjeDQ0Vi1GbGhSNjRxTGwwUlpB)

Smart Contract: [Smart Contract](https://celo-sepolia.blockscout.com/address/0x40f805866f5923b376B5c722767cF17DD5f9d9Cb)

Customer Chat: [Simulation](https://kasicred-28bu.onrender.com/docs#/)

Vendor Dashboard [Basic Dashboard](https://kasicred.onrender.com/)

## The Problem

South Africa's informal sector contributes an estimated 23.7% of GDP, yet most
vendors — roughly 60% classified as cash-only "survivalist" businesses — remain
invisible to formal financial systems. No transaction history, no credit trail,
no way to prove they're worth lending to.

## What KasiCred Does

- A vendor gets a QR code. A buyer scans it after a purchase and is guided
  through a rating flow inside WhatsApp — no app download required.
- Ratings only exist if tied to a verified transaction (no purchase, no rating),
  closing the obvious self-rating loophole.
- Ratings are weighted by transaction size (bounded both ends) and combined
  with buyer repeat-purchase history, to resist gaming.
- Each verified rating is hashed and stored on the Celo blockchain for
  tamper-proof integrity; review content stays off-chain in SQLite to keep
  costs low and the build lightweight.
- Over time, a vendor builds a portable, exportable proof-of-business record —
  something they can show a microlender that doesn't exist today.

## Why Celo

Low gas fees, mobile-first design, and phone-number-linked identity — no
wallet literacy required from vendors who've never touched crypto.

## Why not Yoco Capital's approach

Yoco Capital lends against card-machine transaction history — a model that
requires a POS device and platform trading history. KasiCred is built for
the cash-only, unbanked vendor that model structurally excludes.

## Language Support

English, Setswana, isiZulu (in verification). Vulavula (Lelapa AI) and
Gemma 3n E2B convert multilingual rating data into a plain-language
creditworthiness summary a lender can act on.

## Privacy & POPIA

- No GPS captured — only a vendor-entered market/area name.
- Ledger data is disclosed only to parties the vendor explicitly chooses.
- Raw voice input (where used) is discarded after transcription.
- Hosted africa-south1 where cloud infrastructure is used.

## Status

Pre-selection submission for Geekulcha 2026 (Blockchain for Impact Use
track). Core architecture designed: rating/weighting logic, Celo hashing
flow, SQLite off-chain storage. QR-to-WhatsApp intake flow and full build
begin at the hackathon build weekend if selected.

## Tech Stack

Celo (testnet) · Solidity · Python · SQLite · WhatsApp Business API ·
Gemma 3n E2B · Vulavula (Lelapa AI)

## Team

Nyakallo · Khatisani · Liya — WeThinkCode_

## Core Features & Workflows

1. **Vendor Onboarding (`POST /vendor/register`):**
   * Vendors register their store name, phone number, market/area, and inventory description.
   * Generates a deterministic EVM address and a unique QR payment/rating URI.
2. **Stateful Conversational Survey (`POST /review/phone`):**
   * Step-by-step interactive chat flow: Language Selection ➔ Star Rating (1–5 ⭐) ➔ Optional Comment/Voice Note ➔ Diagnostic Tagging (for ratings $\le 3$).
3. **Gasless On-Chain Settlement (`recordReview`):**
   * Automatically hashes review metadata off-chain and anchors the review hash and score to the Celo Sepolia smart contract via a secure backend relayer[cite: 1, 2, 3].
4. **Live Trust Metrics (`GET /vendor/phone/{phone_or_tag}`):**
   * Instantly queries the deployed smart contract to fetch the verified aggregate average score and total review count for any merchant[cite: 1].

## Local Development & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/nyaks1/KasiCred.git](https://github.com/nyaks1/KasiCred.git)
   cd KasiCred

2. **Install Dependencies:** 
pip install -r requirements.txt

3. **Configure your environment variables (.env):**

```bash
CELO_RPC_URL=[https://forno.celo-sepolia.celo-testnet.org](https://forno.celo-sepolia.celo-testnet.org)
RELAYER_PRIVATE_KEY=your_private_key_here
CONTRACT_ADDRESS=your_deployed_contract_address_here
```

4. **Run the FastAPI server:**
```bash
uvicorn backend.app:app --reload
```

5. **Test the Chatbot Interface**

Open frontend/index.html in your browser to test the interactive WhatsApp chat simulator live against your backend!
