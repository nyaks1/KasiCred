import os

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "kasicred-demo-2026")


@router.get("/webhook/whatsapp")
async def verify(request: Request):
    q = request.query_params
    mode = q.get("hub.mode") or q.get("hub_mode") or ""
    token = q.get("hub.verify_token") or q.get("hub_verify_token") or ""
    challenge = q.get("hub.challenge") or q.get("hub_challenge") or ""

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        # Meta requires the raw challenge as the body — not JSON
        return PlainTextResponse(challenge, status_code=200)

    return PlainTextResponse("verify failed", status_code=403)


@router.post("/webhook/whatsapp")
async def inbound(request: Request):
    body = await request.json()
    print("WEBHOOK", body, flush=True)

    try:
        entry = body.get("entry") or [{}]
        changes = entry[0].get("changes") or [{}]
        value = changes[0].get("value") or {}
        messages = value.get("messages") or []
        if messages:
            msg = messages[0]
            print(
                f"MSG from={msg.get('from')} type={msg.get('type')} "
                f"text={(msg.get('text') or {}).get('body')}",
                flush=True,
            )
    except Exception as e:
        print("parse error", e, flush=True)

    return {"status": "ok"}
