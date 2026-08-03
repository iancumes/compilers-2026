#!/bin/bash
set -euo pipefail

: "${VERCEL_TOKEN:?VERCEL_TOKEN is required}"

PROJECT_NAME="${SITE_NAME:-lab3-sitelang-ian-cumes}"
TEAM_QUERY=""
if [ -n "${VERCEL_TEAM_ID:-}" ]; then
  TEAM_QUERY="?teamId=$VERCEL_TEAM_ID"
fi

cat > /tmp/index.html <<'EOF'
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SiteLang API Explorer</title></head>
<body style="font-family:system-ui;background:#07111f;color:#e7eef7;display:grid;place-items:center;min-height:100vh;margin:0">
  <main style="max-width:680px;padding:2rem;text-align:center">
    <h1 style="color:#63e6be">Deployment creado con la API de Vercel</h1>
    <p>Esta es la prueba directa de la Parte 1. No se utilizo el dashboard ni la CLI para publicar el archivo.</p>
  </main>
</body>
</html>
EOF

HTML_CONTENT=$(cat /tmp/index.html)
jq -n --arg name "$PROJECT_NAME" --arg html "$HTML_CONTENT" \
  '{name: $name, files: [{file: "index.html", data: $html}], projectSettings: {framework: null}, target: "production"}' \
  > /tmp/vercel-deployment.json

curl --fail-with-body -sS -X POST \
  -H "Authorization: Bearer $VERCEL_TOKEN" -H "Content-Type: application/json" \
  --data-binary @/tmp/vercel-deployment.json \
  "https://api.vercel.com/v13/deployments$TEAM_QUERY" > /tmp/vercel-result.json

DEPLOYMENT_ID=$(jq -r '.id' /tmp/vercel-result.json)
for attempt in $(seq 1 45); do
  STATE=$(jq -r '.readyState // .state // "QUEUED"' /tmp/vercel-result.json)
  if [ "$STATE" = "READY" ]; then
    URL=$(jq -r 'if (.alias | type) == "array" and (.alias | length) > 0 then .alias[0] else .url end' /tmp/vercel-result.json)
    echo "[OK] Vercel deployment READY: https://$URL"
    exit 0
  fi
  if [ "$STATE" = "ERROR" ] || [ "$STATE" = "CANCELED" ]; then
    echo "Vercel deployment ended in state $STATE" >&2
    exit 1
  fi
  sleep 2
  curl --fail-with-body -sS -H "Authorization: Bearer $VERCEL_TOKEN" \
    "https://api.vercel.com/v13/deployments/$DEPLOYMENT_ID$TEAM_QUERY" > /tmp/vercel-result.json
done

echo "Vercel deployment did not become READY within 90 seconds." >&2
exit 1
