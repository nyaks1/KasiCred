# Research brief — GKHACK26 (Sonke / gklink) 72-hour hackathon

> Date: 2026-09-24 (Thursday) · depth: **standard** · workspace: `research/gkhack26/`
> Event window (user-stated): **Fri 2026-09-25 → Sun 2026-09-27** (starts tomorrow, ends Sunday)

## Refined question

What does **GKHACK26** actually require (theme, deliverables, sponsors, judging), and what is the **fastest legal path** to a WhatsApp-based **proof-of-income** demo for informal SA vendors **without a BSP / without a middleman**, framed as proof-of-income (not a credit score) under POPIA/NCR?

Audience: Nyakallo (KasiCred / WeThinkCode_) + team. Decision at stake: **what to build in the next 72 hours** that scores on the real rubric and does not get disqualified.

## Scope

**In**
- Official event page: https://sonke.gklink.co/event/gkhack26 — theme, problem statement (verbatim), rules, mandatory deliverables, video/repo requirements, team size, eligibility, judging rubric if published
- Sponsors being revealed (BBD, Telkom, “and more”): sponsor tracks, required tech, prizes, what judges reward
- WhatsApp integration without BSP: Meta WhatsApp Cloud API direct vs BSP (360dialog, Twilio, MessageBird, Infobip), unofficial libraries (Baileys, whatsapp-web.js) ToS/ban risk, webhook architecture, free tiers, setup time to first message in ≤72h
- **Proof-of-income ≠ credit score** framing: SA legal treatment (NCA/NCR vs income verification), POPIA (processing, special personal info, s71), what “proof of income” evidence can be for informal vendors
- Concrete 72h build path for KasiCred-shaped product reframed as POI attestation + WhatsApp UX
- Past winners / judging patterns of this series or similar SA student hackathons if findable

**Out**
- Full production WhatsApp Business compliance programme
- Building code in this research phase
- Credit scoring model design (explicitly out of product frame)
- Non-SA regulatory regimes

## Assumptions

1. Event dates per user: 3 days, **25–27 Sep 2026**. Verify on the official page; if different, official wins.
2. Product frame is **proof of income / trade evidence for informal vendors**, **not** a credit score or Loan Ready underwriting number.
3. Constraint is hard: **no BSP, no middleman** on the WhatsApp path (user requirement).
4. Existing asset: KasiCred prototype (FastAPI + SQLite + Celo hash + vendor dashboard + WhatsApp state machine).
5. Sponsors known so far: **BBD**, **Telkom**; others TBD on the event site.
6. Depth **standard** (time-boxed to 72h before the event): 4 sub-agents, 6 queries each, 1 follow-up round max.

## Angles

- **F1** — GKHACK26 official brief: theme/problem verbatim, rules, deliverables, schedule, team, judging, prizes
- **F2** — Sponsors (BBD, Telkom, others): tracks, required SDKs/tech, what they score, disqualification risks
- **F3** — WhatsApp without BSP / no middleman: official architecture options, unofficial risk, free tier, time-to-first-webhook
- **F4** — Proof-of-income (not credit score) + 72h ship plan: SA legal frame (POPIA/NCR), evidence types for informal vendors, demo path

## Query budget

Standard mode: **6** searches per sub-agent. Sources target: **15+**.

## Hard gates before build (Hackathon Framework Phase 0/4 — do not skip in final report)

- Exact problem/theme word-for-word + one-sentence trace of the idea to it
- Mandatory deliverables list + disqualification flags
- Cold-machine check plan (fresh clone / deploy / video from a clean window)
- If sponsor tech is mandatory: load-bearing or bolted-on?
