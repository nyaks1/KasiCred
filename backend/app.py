import hashlib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.celo_client import (
    verify_connection,
    get_vendor_summary,
    record_review_onchain
)

app = FastAPI(
    title="KasiCred Ledger API",
    description="Celo Sepolia Testnet Integration Service"
)

class ReviewPayload(BaseModel):
    vendor_address: str
    review_text: str
    score: int

@app.get("/")
def root():
    return {"status": "online", "service": "KasiCred Celo Testnet Adapter"}

@app.get("/chain/status")
def chain_status():
    status = verify_connection()
    if not status["connected"]:
        raise HTTPException(status_code=503, detail="Unable to connect to Celo RPC")
    return status

@app.get("/vendor/{vendor_address}")
def read_vendor(vendor_address: str):
    try:
        return get_vendor_summary(vendor_address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/review")
def post_review(payload: ReviewPayload):
    if not (1 <= payload.score <= 5):
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
    
    review_hash = hashlib.sha256(payload.review_text.encode()).digest()
    
    try:
        tx_hash = record_review_onchain(
            payload.vendor_address,
            review_hash,
            payload.score
        )
        return {
            "status": "committed",
            "tx_hash": tx_hash,
            "explorer_url": f"https://celo-sepolia.blockscout.com/tx/{tx_hash}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))