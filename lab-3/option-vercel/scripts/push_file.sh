#!/bin/bash
set -euo pipefail

: "${GITHUB_TOKEN:?GITHUB_TOKEN is required}"
[ -f repo_full_name.txt ] || { echo "Run create_repo.sh first." >&2; exit 1; }

FULL_NAME=$(cat repo_full_name.txt)
API="https://api.github.com"
ENDPOINT="$API/repos/$FULL_NAME/contents/index.html"
HEADERS=(-H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")

cat > /tmp/index.html <<'EOF'
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SiteLang API Explorer</title></head>
<body style="font-family:system-ui;background:#07111f;color:#e7eef7;display:grid;place-items:center;min-height:100vh;margin:0">
  <main style="max-width:680px;padding:2rem;text-align:center">
    <h1 style="color:#63e6be">Archivo publicado con la API de GitHub</h1>
    <p>Esta pagina es la prueba de la Parte 1. El compilador SiteLang la reemplazara con el sitio final.</p>
  </main>
</body>
</html>
EOF

STATUS=$(curl -sS -o /tmp/current-file.json -w "%{http_code}" "${HEADERS[@]}" "$ENDPOINT")
SHA=""
if [ "$STATUS" = "200" ]; then
  SHA=$(jq -r '.sha' /tmp/current-file.json)
elif [ "$STATUS" != "404" ]; then
  jq -r '.message // "Unknown GitHub error"' /tmp/current-file.json >&2
  exit 1
fi

CONTENT=$(base64 -w 0 /tmp/index.html)
jq -n --arg message "Publish API explorer page" --arg content "$CONTENT" --arg sha "$SHA" \
  '{message: $message, content: $content,
    committer: {name: "iancumes", email: "87866288+iancumes@users.noreply.github.com"},
    author: {name: "iancumes", email: "87866288+iancumes@users.noreply.github.com"}}
   + (if $sha == "" then {} else {sha: $sha} end)' > /tmp/update-file.json

curl --fail-with-body -sS -X PUT "${HEADERS[@]}" -H "Content-Type: application/json" \
  --data-binary @/tmp/update-file.json "$ENDPOINT" > /tmp/file-result.json

echo "[OK] File: $(jq -r '.content.html_url' /tmp/file-result.json)"
