# KasiCred product framing (source of truth for the hack)

> Owner: Nyakallo · Audience: full team (Khatisani, Liya) · Event: GKHack26, BCX Centurion, 25–27 Sep 2026  
> Read this **before** you write code, slides, or a README pitch. This overrides any older “credit score / Loan Ready” language.

---

## 1. What we are proving

**Not** a credit score. **Not** Loan Ready. **Not** “Google Reviews for spaza shops.”

We are building a **proof-of-income pack** for informal traders who have real cash trade and zero paper trail a lender will accept.

**One sentence (say this out loud until it’s boring):**

> Thandi sells vetkoek at the taxi rank — no payslip, no bureau file. On WhatsApp, in minutes, she builds a proof-of-income pack a microlender can actually trust. **We don’t score her. We prove her.**

Theme fit (GKHack26 **BUILD FOR USE**): would a real user trust and use this?  
→ Trader already has WhatsApp. Lender already wants to lend. We remove the documentation wall.

---

## 2. The business model (this is the company)

| Party | Pays? | Gets |
|---|---|---|
| **Trader / vendor** | **R0 — always free** | WhatsApp intake + their own PDF pack |
| **Microlender** | **PAYS — this is revenue** | Verified fetch of *this applicant’s* pack |
| Landlord | Same paid fetch (secondary) | Nice hook for the story — **not** the primary wallet |

**Who pays for the PDF? The microlender who already wants to lend.**  
Not the trader. Not “the public.” Not a subscription to browse people.

**When they pay:** at application / underwriting — when they must decide on someone in front of them.

**They do not pay** to “see how another is doing.” That is a scoreboard. That is NCR + POPIA fire.

### Money line (use in slides)

> Free proof for the trader. **Paid truth for the lender.**  
> One thin-file enquiry wastes more than we charge per pack.

### Price sketch (hackathon / pilot)

- Per pack fetch: **R25–R80** (land at **R40** unless research forces otherwise)
- Desk plan later: e.g. R2 000 / 100 credits
- Landlord vertical = same SKU, not a second product

---

## 3. Product surfaces

### A. WhatsApp (trader side) — no BSP, no middleman

Meta **WhatsApp Cloud API** only (Graph + webhooks).  
**Never** Baileys / whatsapp-web.js / venom (ToS / ban risk).

Flow:

1. POPIA **s18 notice + consent** (first messages — non-negotiable)
2. Collect evidence: till slips · stokvel books · short trade log · buyer attestations · optional affidavit
3. Output: **Proof-of-Income Pack** (PDF + timestamps + consent log + fingerprint)

### B. Verify web page (lender side) — where money happens

Not a public directory.

1. Trader receives a **share code / short link** (they control it; expiry e.g. 72h)
2. Lender opens verify page → enters code
3. Sees summary + fingerprint + consent timestamp
4. **Pays** → full PDF / download
5. Every fetch is logged and visible to the trader

Demo path (90 seconds): **one trader → one code → one paid fetch**.

### C. Blockchain = the seal, not the product

Your mates on chain are building the **wax seal**, not the storefront.

- What goes on-chain: **hash** of evidence + consent log (integrity / tamper-evident)
- What stays off-chain: PII, photos, review text (SQLite / files)
- Relayer signs; **vendor never touches a wallet or gas**
- Sponsors/judges hear: *“Blockchain is the lock on the document, not the pitch.”*

If the first word of the pitch is “blockchain” or “decentralised,” rewrite the pitch.

---

## 4. What we cut (dead weight)

| Cut | Why |
|---|---|
| Trust score / Loan Ready / 0–100 | Looks like unlicensed scoring (NCA / NCR) + fails BUILD FOR USE |
| “AI-powered” anything | Organisers: AI is **not** impressive this year |
| Public “browse vendors” grid | POPIA disaster + illegal-bureau smell |
| Consumer score subscriptions | Free elsewhere (Experian Up etc.) — B2C is a trap |
| Bolted-on Telkom/BBD logos | Only use sponsor tech if it is **load-bearing** |
| Quantum as the hero | Max **5 bonus pts**; ≤2h only after POI demo is green |

---

## 5. Legal / POPIA (say it if a security mentor asks)

- **Income evidence ≠ lending.** We do not grant credit (NCA s40 threshold is R0 for providers — we are not one).
- **We do not market as a credit bureau** (NCA s43 / s157C). Applicant-initiated, purpose-limited pack — not a multi-consumer report shop.
- **POPIA:** income is ordinary personal information (not special PI). Still required: s18 notice, consent (s11), minimality (s10), short retention (s14), deletion path.
- **NCA s78(3):** irregular income still counts. That is the statutory tailwind for informal POI.
- Lender still does affordability under **NCA s81** — we supply evidence, they decide.

---

## 6. Competitive frame (2 minutes)

Unlike **CommuScore** (stokvel SaaS → score, deadpooled) and bank payslip POI (useless for cash trade):

> We produce a **vendor-consented income evidence pack** on WhatsApp, **tamper-evident**, sold as **paid fetch to the microlender** — not a score, not a free directory.

Read more: `research/commuscore-blueprint/REPORT.md` · `research/gkhack26/REPORT.md`

---

## 7. Stage script (90s)

1. **Hook:** landlord / lender cannot see cash income → good traders get denied.  
2. **Villain:** payslips and bureau files.  
3. **Hero:** WhatsApp POI pack, trader-controlled share code.  
4. **Why now:** NCA counts irregular income; POPIA wants explicit consent; WhatsApp is universal.  
5. **Demo:** consent → photo → pack → **lender pays to open**.  
6. **Ask:** pilot with one microlending desk; R40 per verified pack.  
7. **Close:** “We don’t score her. We prove her.”

---

## 8. Standing rules for the weekend

1. **Build the man** — trader gets dignity + a document, free.  
2. **Sell the shovel** — microlender pays for the fetch.  
3. Cold-machine before freeze (fresh clone → env → `/` → one full POI → PDF).  
4. Fork, don’t only clone (team visibility).  
5. 2-hour hard freeze before Sunday deadline — no new features.

*This document is the product contract. If code or slides disagree with this file, the file wins.*
