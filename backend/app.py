import hashlib
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3

from backend.celo_client import (
    CONTRACT_ADDRESS,
    get_vendor_summary,
    record_review_onchain,
    verify_connection,
)

app = FastAPI(
    title="KasiCred Trust Engine",
    description="Maps human identifiers to on-chain Celo Sepolia trust records and manages vendor registration.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def phone_to_vendor_address(phone_or_tag: str) -> str:
    """Deterministic hash mapping phone/store ID to EVM address."""
    clean_id = phone_or_tag.strip().replace(" ", "").lower()
    hash_bytes = hashlib.sha256(clean_id.encode()).digest()
    return Web3.to_checksum_address("0x" + hash_bytes[-20:].hex())


# =====================================================================
# Off-Chain In-Memory Storage & Registries
# =====================================================================

vendor_database: Dict[str, dict] = {
    "0712345678": {
        "store_name": "Mama Thabo's Spaza",
        "phone_number": "0712345678",
        "market_area": "Randburg Taxi Rank",
        "category_items": "Fresh produce, snacks, and cold drinks"
    }
}

user_sessions: Dict[str, dict] = {}

PROMPTS = {
    "1": {
        "welcome": "Welcome to KasiCred! Let's get '{vendor}' ready for credit building.\n\nSelect Language:\n1. English\n2. isiZulu\n3. Setswana",
        "rating": "How was your experience with {vendor}? 1-5 ⭐ (single tap/number reply)",
        "comment": "Want to add a quick comment? Reply with text or a voice note, or type 'skip'.",
        "feedback_low": "Sorry to hear that — what went wrong?\n(short options: quality / price / service / other)",
        "complete": "Thanks! Your rating helps '{vendor}' build their credit profile.",
    },
    "2": {
        "welcome": "Siyakwamukela ku-KasiCred! Masilungiselele i-'{vendor}' ukwakha isikweletu.\n\nKhetha Ulimi:\n1. English\n2. isiZulu\n3. Setswana",
        "rating": "Ibinjani inkonzo kwa-{vendor}? 1-5 ⭐ (phendula ngenombolo)",
        "comment": "Uyafuna ukushiya umbono omfushane? Thumela umbhalo, i-voice note, noma bhala 'skip'.",
        "feedback_low": "Siyaxolisa ukuzwa lokho — konakelephi?\n(khetha: quality / price / service / other)",
        "complete": "Siyabonga! Isilinganiso sakho sisiza '{vendor}' ukwakha iphrofayili yesikweletu.",
    },
    "3": {
        "welcome": "O amogetswe mo KasiCred! A re thuse '{vendor}' go aga sekoloto sa kgwebo.\n\nKgetha Puo:\n1. English\n2. isiZulu\n3. Setswana",
        "rating": "Maitemogelo a gago a ntse jang le {vendor}? 1-5 ⭐ (araba ka nomoro)",
        "comment": "A o batla go tlogela maikutlo? Romela molaetsa, voice note, kgotsa kwala 'skip'.",
        "feedback_low": "Re maswabi go utlwa seo — molato e ne e le eng?\n(kgetha: quality / price / service / other)",
        "complete": "Re a leboga! Dinaledi tsa gago di thusa '{vendor}' go aga rekoto ya kgwebo.",
    },
}


# =====================================================================
# Request Schemas
# =====================================================================

class VendorRegistrationPayload(BaseModel):
    store_name: str
    phone_number: str
    market_area: str
    category_items: str


class UnifiedReviewPayload(BaseModel):
    phone: str
    message: Optional[str] = None
    media_url: Optional[str] = None
    vendor_name: Optional[str] = "Mama Thabo's Spaza"
    vendor_phone_or_tag: Optional[str] = "0712345678"
    review_text: Optional[str] = None
    score: Optional[int] = None


# =====================================================================
# API Endpoints
# =====================================================================

@app.get("/")
def root():
    return {"service": "KasiCred Relayer", "status": "online"}


@app.get("/chain/status")
def chain_status():
    return verify_connection()


@app.post("/vendor/register")
def register_vendor(payload: VendorRegistrationPayload):
    clean_phone = payload.phone_number.strip().replace(" ", "").lower()
    mapped_address = phone_to_vendor_address(clean_phone)

    profile = {
        "store_name": payload.store_name.strip(),
        "phone_number": clean_phone,
        "market_area": payload.market_area.strip(),
        "category_items": payload.category_items.strip(),
        "mapped_onchain_address": mapped_address,
        "qr_payment_uri": f"kasicred://rate/{clean_phone}"
    }

    vendor_database[clean_phone] = profile

    return {
        "status": "success",
        "message": f"Stall '{payload.store_name}' registered successfully!",
        "profile": profile
    }


@app.get("/vendor/phone/{phone_or_tag}")
def get_vendor_by_phone(phone_or_tag: str):
    clean_id = phone_or_tag.strip().replace(" ", "").lower()
    vendor_address = phone_to_vendor_address(clean_id)

    profile = vendor_database.get(clean_id, {
        "store_name": "Unregistered Stall",
        "phone_number": clean_id,
        "market_area": "Unknown",
        "category_items": "General Merchandise",
        "mapped_onchain_address": vendor_address
    })

    try:
        onchain_summary = get_vendor_summary(vendor_address)
        return {
            "profile": profile,
            "contract_address": CONTRACT_ADDRESS,
            "trust_metrics": onchain_summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/review/phone")
def submit_vendor_review(payload: UnifiedReviewPayload):
    # Direct Submission Path
    if payload.score is not None and payload.review_text is not None:
        if not (1 <= payload.score <= 5):
            raise HTTPException(status_code=400, detail="Score must be between 1 and 5.")

        vendor_identifier = payload.vendor_phone_or_tag or payload.phone
        vendor_address = phone_to_vendor_address(vendor_identifier)
        review_hash = hashlib.sha256(payload.review_text.encode()).digest()

        try:
            tx_hash = record_review_onchain(
                vendor_address=vendor_address,
                review_hash=review_hash,
                score=payload.score,
            )
            return {
                "status": "success",
                "vendor": vendor_identifier,
                "mapped_address": vendor_address,
                "score": payload.score,
                "tx_hash": tx_hash,
                "explorer_url": f"https://celo-sepolia.blockscout.com/tx/{tx_hash}",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Conversational WhatsApp Survey Path
    phone_key = payload.phone.strip().replace(" ", "").lower()
    raw_message = (payload.message or "").strip()
    clean_message = raw_message.lower()

    if phone_key not in user_sessions:
        target_vendor_phone = (payload.vendor_phone_or_tag or "0712345678").strip().replace(" ", "").lower()
        registered_vendor = vendor_database.get(target_vendor_phone)
        display_name = registered_vendor["store_name"] if registered_vendor else (payload.vendor_name or "Mama Thabo's Spaza")

        user_sessions[phone_key] = {
            "step": "LANGUAGE_SELECT",
            "vendor_name": display_name,
            "vendor_phone_or_tag": target_vendor_phone,
            "language": "1",
            "score": None,
            "comment": None,
            "issue": None,
        }
        return {
            "reply": PROMPTS["1"]["welcome"].format(vendor=display_name),
            "step": "LANGUAGE_SELECT",
        }

    session = user_sessions[phone_key]
    lang = session.get("language", "1")
    prompts = PROMPTS[lang]

    if session["step"] == "LANGUAGE_SELECT":
        if clean_message in ["1", "2", "3"]:
            session["language"] = clean_message
            session["step"] = "RATING"
            selected_prompts = PROMPTS[clean_message]
            return {
                "reply": selected_prompts["rating"].format(vendor=session["vendor_name"]),
                "step": "RATING",
            }
        return {
            "reply": "Please select a valid option (1, 2, or 3):\n1. English\n2. isiZulu\n3. Setswana",
            "step": "LANGUAGE_SELECT",
        }

    if session["step"] == "RATING":
        if clean_message in ["1", "2", "3", "4", "5"]:
            session["score"] = int(clean_message)
            session["step"] = "COMMENT"
            return {
                "reply": prompts["comment"],
                "step": "COMMENT",
            }
        return {
            "reply": "Please reply with a valid rating: 1-5 ⭐",
            "step": "RATING",
        }

    if session["step"] == "COMMENT":
        if payload.media_url:
            session["comment"] = f"[Voice Note: {payload.media_url}]"
        elif clean_message != "skip":
            session["comment"] = raw_message

        if session["score"] <= 3:
            session["step"] = "FEEDBACK_REASON"
            return {
                "reply": prompts["feedback_low"],
                "step": "FEEDBACK_REASON",
            }
        return commit_survey_to_celo(phone_key, session, prompts)

    if session["step"] == "FEEDBACK_REASON":
        valid_reasons = ["quality", "price", "service", "other"]
        matched_reason = next((r for r in valid_reasons if r in clean_message), "other")
        session["issue"] = matched_reason
        return commit_survey_to_celo(phone_key, session, prompts)


def commit_survey_to_celo(phone_key: str, session: dict, prompts: dict) -> dict:
    """Computes review hash, records to Celo Sepolia, and clears session."""
    vendor_identifier = session["vendor_phone_or_tag"]
    vendor_address = phone_to_vendor_address(vendor_identifier)
    score = session["score"]

    comment = session.get("comment") or ""
    issue = session.get("issue") or ""
    metadata_string = f"{score}|{comment}|{issue}|{phone_key}"
    review_hash = hashlib.sha256(metadata_string.encode()).digest()

    tx_hash = None
    try:
        tx_hash = record_review_onchain(
            vendor_address=vendor_address,
            review_hash=review_hash,
            score=score,
        )
    except Exception as e:
        print(f"[Celo Relay Warning] On-chain push failed: {e}")

    vendor_name = session["vendor_name"]
    del user_sessions[phone_key]

    return {
        "reply": prompts["complete"].format(vendor=vendor_name),
        "status": "COMPLETED",
        "onchain_recorded": bool(tx_hash),
        "transaction_hash": tx_hash,
        "explorer_url": f"https://celo-sepolia.blockscout.com/tx/{tx_hash}" if tx_hash else None,
    }