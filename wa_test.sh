#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
# shellcheck disable=SC1091
. ./.env
set +a

PHONE_ID="${PHONE_NUMBER_ID:-1321205064412906}"
TO="27785933331"
TOKEN="${WHATSAPP_TOKEN:?WHATSAPP_TOKEN missing in .env}"

echo "== SEND =="
curl -sS -X POST "https://graph.facebook.com/v25.0/${PHONE_ID}/messages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"messaging_product\":\"whatsapp\",\"to\":\"${TO}\",\"type\":\"text\",\"text\":{\"body\":\"KasiCred online (system token)\"}}"
echo
echo "== TOKEN CHECK =="
curl -sS "https://graph.facebook.com/v25.0/me?access_token=${TOKEN}"
echo
