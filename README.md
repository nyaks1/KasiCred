# KasiCred

Blockchain-based trust and credit ledger for informal street vendors in South Africa.

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