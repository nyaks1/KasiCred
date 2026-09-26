import io
import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

from backend.poi_conversation import handle_media, handle_message, start_deep_link, start_payload
from backend.sales_qr import buyer_confirm_message, get_sale, new_sale

router = APIRouter()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "kasicred-demo-2026")
TOKEN = os.getenv("WHATSAPP_TOKEN") or os.getenv("WHATSAPP_ACCESS_TOKEN") or ""
PHONE_ID = os.getenv("PHONE_NUMBER_ID") or os.getenv("WHATSAPP_PHONE_NUMBER_ID") or ""
DEFAULT_E164 = os.getenv("WHATSAPP_PUBLIC_E164", "15551771178")


def _parse_inbound(body: dict) -> tuple[str | None, str, bool]:
    """Return (from, text, is_media)."""
    try:
        entry = body.get("entry") or [{}]
        changes = entry[0].get("changes") or [{}]
        value = changes[0].get("value") or {}
        messages = value.get("messages") or []
        if not messages:
            return None, "", False
        msg = messages[0]
        sender = msg.get("from")
        mtype = msg.get("type") or ""
        if mtype == "text":
            return sender, (msg.get("text") or {}).get("body") or "", False
        if mtype in ("image", "audio", "document", "video", "sticker"):
            return sender, "", True
        return sender, "", False
    except Exception:
        return None, "", False


async def _send_text(to: str, body: str) -> None:
    if not TOKEN or not PHONE_ID:
        print(f"NO_TOKEN would send to={to}: {body[:80]}", flush=True)
        return
    import httpx

    url = f"https://graph.facebook.com/v25.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, headers=headers)
        print(f"SEND {to} status={r.status_code} body={r.text[:200]}", flush=True)


@router.post("/api/sale")
async def record_sale(request: Request):
    """Vendor records a sale -> QR appears on their phone for the buyer to scan."""
    body = await request.json()
    vendor_phone = str(body.get("vendor_phone") or body.get("phone") or "").strip()
    amount = body.get("amount") or body.get("amount_rands") or 0
    note = str(body.get("note") or "")
    if not vendor_phone or not amount:
        return JSONResponse({"error": "vendor_phone and amount required"}, status_code=400)
    return JSONResponse(new_sale(vendor_phone, float(amount), note=note))


@router.get("/api/sale/{sale_id}")
async def sale_status(sale_id: str):
    sale = get_sale(sale_id)
    if not sale:
        return JSONResponse({"error": "not found"}, status_code=404)
    return JSONResponse({k: sale[k] for k in sale if k != "buyer_phone" or sale.get("status") == "confirmed"})


@router.get("/sale/{sale_id}/qr.svg")
async def sale_qr_svg(sale_id: str):
    """On-screen QR for this sale only — not a printed sticker."""
    sale = get_sale(sale_id)
    if not sale:
        return PlainTextResponse("sale not found", status_code=404)
    link = f"https://wa.me/{DEFAULT_E164}?text=CONFIRM%20{sale_id}"
    return Response(content=_qr_svg(link), media_type="image/svg+xml")


@router.get("/api/whatsapp/start")
async def whatsapp_start():
    """Field/demo entry point — returns the wa.me deep link for the vendor."""
    return JSONResponse(start_payload())


def _qr_svg(data: str, scale: int = 6) -> str:
    import segno

    qr = segno.make(data, error="m")
    # compact SVG for embedding in the join page
    buff = io.BytesIO()
    qr.save(buff, kind="svg", scale=scale, border=2, dark="#0B1A10", light="#F5F0E6", xmldecl=False, svgns=False)
    return buff.getvalue().decode("utf-8")


@router.get("/whatsapp/qr.svg")
async def whatsapp_qr_svg():
    """QR that opens WhatsApp with 'hi' ready — sticker / slide / join page."""
    svg = _qr_svg(start_deep_link())
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/whatsapp/qr.png")
async def whatsapp_qr_png():
    import segno

    buff = io.BytesIO()
    segno.make(start_deep_link(), error="m").save(buff, kind="png", scale=8, border=2)
    return Response(content=buff.getvalue(), media_type="image/png")


@router.get("/whatsapp/join")
async def whatsapp_join():
    """One-tap page for stickers / reviewer phone: open this, press the button."""
    info = start_payload()
    url = info["url"]
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>KasiCred — Start Proof of Income</title>
<style>
  body {{ font-family: system-ui, sans-serif; background:#14171A; color:#F5F0E6;
         margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px; }}
  .card {{ background:#1E2226; border:1px solid #2B3036; border-radius:16px; padding:28px; max-width:360px; text-align:center; }}
  a.btn {{ display:inline-block; margin-top:18px; background:#25D366; color:#0B1A10; text-decoration:none;
           font-weight:700; padding:14px 22px; border-radius:10px; font-size:16px; }}
  .muted {{ opacity:.65; font-size:12px; margin-top:14px; line-height:1.5; }}
</style></head>
<body>
  <div class="card">
    <div style="font-size:22px; font-weight:700;">Kasi<span style="color:#F2A93B">Cred</span></div>
    <p style="font-size:14px; line-height:1.5;">Proof of income on WhatsApp.<br/>You start. We never cold-message.</p>
    <a class="btn" href="{url}">Chat on WhatsApp</a>
    <div style="margin-top:18px;">
      <img src="/whatsapp/qr.svg" alt="QR to start KasiCred on WhatsApp" width="180" height="180" />
    </div>
    <div class="muted">
      Opens WhatsApp with “hi” ready to send.<br/>
      POPIA consent comes first. Not a credit score.
    </div>
  </div>
</body></html>"""
    return HTMLResponse(html)


@router.get("/webhook/whatsapp")
async def verify(request: Request):
    q = request.query_params
    mode = q.get("hub.mode") or q.get("hub_mode") or ""
    token = q.get("hub.verify_token") or q.get("hub_verify_token") or ""
    challenge = q.get("hub.challenge") or q.get("hub_challenge") or ""
    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return PlainTextResponse(challenge, status_code=200)
    return PlainTextResponse("verify failed", status_code=403)


@router.post("/webhook/whatsapp")
async def inbound(request: Request):
    body = await request.json()
    print("WEBHOOK", body, flush=True)
    sender, text, is_media = _parse_inbound(body)
    if sender:
        if is_media:
            reply = handle_media(sender)
        else:
            reply = buyer_confirm_message(sender, text)
            if reply is None:
                reply = handle_message(sender, text)
        print(f"REPLY to {sender}: {reply[:120]}", flush=True)
        await _send_text(sender, reply)
    return {"status": "ok"}
