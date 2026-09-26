#!/usr/bin/env bash
set -euo pipefail
TOKEN="${1:?usage: wa_check.sh TOKEN}"
APP_ID="1083387547784687"
WABA_ID="1351463993476605"
PN_ID="1321205064412906"
CALLBACK="https://gown-denial-directly.ngrok-free.dev/webhook/whatsapp"

echo "== 1) Local challenge via ngrok =="
curl -sS "${CALLBACK}?hub.mode=subscribe&hub.verify_token=kasicred-demo-2026&hub.challenge=12345"
echo
echo

echo "== 2) App subscriptions =="
curl -sS "https://graph.facebook.com/v25.0/${APP_ID}/subscriptions?access_token=${TOKEN}"
echo
echo

echo "== 3) WhatsApp account fields (webhook override / phone) =="
curl -sS "https://graph.facebook.com/v25.0/${WABA_ID}/?fields=name,verification_status&access_token=${TOKEN}"
echo
echo

echo "== 4) Phone number status =="
curl -sS "https://graph.facebook.com/v25.0/${PN_ID}?fields=display_phone_number,status,quality_rating,code_verification_status&access_token=${TOKEN}"
echo
echo

echo "== 5) App owned apps / configs hint =="
curl -sS "https://graph.facebook.com/v25.0/${APP_ID}/app_event_hosts?access_token=${TOKEN}"
echo
