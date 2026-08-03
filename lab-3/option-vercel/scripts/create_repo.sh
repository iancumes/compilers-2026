#!/bin/bash
set -euo pipefail

: "${GITHUB_TOKEN:?GITHUB_TOKEN is required}"

REPO_NAME="${SITE_NAME:-lab3-sitelang-ian-cumes}"
DESCRIPTION="Sitio generado por SiteLang para el Laboratorio 3 de Compiladores"
API="https://api.github.com"
HEADERS=(-H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")

LOGIN=$(curl --fail-with-body -sS "${HEADERS[@]}" "$API/user" | jq -r '.login')
FULL_NAME="$LOGIN/$REPO_NAME"

echo "[*] Checking GitHub repository $FULL_NAME..."
STATUS=$(curl -sS -o /tmp/repository.json -w "%{http_code}" "${HEADERS[@]}" "$API/repos/$FULL_NAME")

if [ "$STATUS" = "404" ]; then
  jq -n --arg name "$REPO_NAME" --arg description "$DESCRIPTION" \
    '{name: $name, description: $description, private: false, auto_init: false}' > /tmp/create-repository.json
  curl --fail-with-body -sS -X POST "${HEADERS[@]}" \
    -H "Content-Type: application/json" \
    --data-binary @/tmp/create-repository.json "$API/user/repos" > /tmp/repository.json
  echo "[OK] Repository created."
elif [ "$STATUS" = "200" ]; then
  echo "[OK] Repository already exists; it will be reused."
else
  jq -r '.message // "Unknown GitHub error"' /tmp/repository.json >&2
  exit 1
fi

REPO_URL=$(jq -r '.html_url' /tmp/repository.json)
echo "$FULL_NAME" > repo_full_name.txt
echo "[OK] Repository: $REPO_URL"
