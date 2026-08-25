import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3
from backend.celo_client import (
    verify_connection,
    get_vendor_summary,
    record_review_onchain
)

app = FastAPI(
    title="KasiCred Trust Engine",
    description="Maps human identifiers to on-chain Celo Sepolia trust records."
)

def phone_to_vendor_address(phone_or_tag: str) -> str:
    """Deterministic hash mapping phone/store ID to EVM address."""
    clean_id = phone_or_tag.strip().replace(" ", "").lower()
    hash_bytes = hashlib.sha256(clean_id.encode()).digest()
    return Web3.to_checksum_address("0x" + hash_bytes[-20:].hex())

class HumanReviewPayload(BaseModel):
    vendor_phone_or_tag: str  # e.g., "+27821234567" or "mama-spaza-01"
    review_text: str          # e.g., "Always delivers fresh stock on time"
    score: int                # 1 to 5

@app.get("/")
def root():
    return {"service": "KasiCred Relayer", "status": "online"}

@app.get("/chain/status")
def chain_status():
    return verify_connection()

@app.get("/vendor/phone/{phone_or_tag}")
def get_vendor_by_phone(phone_or_tag: str):
    """Retrieve on-chain trust score using only the vendor's phone number or ID."""
    vendor_address = phone_to_vendor_address(phone_or_tag)
    try:
        data = get_vendor_summary(vendor_address)
        return {
            "identifier": phone_or_tag,
            "mapped_onchain_address": vendor_address,
            "trust_metrics": data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/review/phone")
def submit_vendor_review(payload: HumanReviewPayload):
    """Submits review on-chain without the user ever managing crypto or wallets."""
    if not (1 <= payload.score <= 5):
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5.")

    vendor_address = phone_to_vendor_address(payload.vendor_phone_or_tag)
    review_hash = hashlib.sha256(payload.review_text.encode()).digest()

    try:
        tx_hash = record_review_onchain(
            vendor_address=vendor_address,
            review_hash=review_hash,
            score=payload.score
        )
        return {
            "status": "success",
            "vendor": payload.vendor_phone_or_tag,
            "mapped_address": vendor_address,
            "score": payload.score,
            "tx_hash": tx_hash,
            "explorer_url": f"https://celo-sepolia.blockscout.com/tx/{tx_hash}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))