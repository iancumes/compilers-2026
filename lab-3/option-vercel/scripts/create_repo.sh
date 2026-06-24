#!/bin/bash
set -e

REPO_NAME="my-portfolio-api-test"
DESCRIPTION="Testing the GitHub API directly with curl — UVG Compiladores 2026"

echo "[*] Calling the GitHub REST API to create a repository..."
echo "[*] Repo name: $REPO_NAME"
echo ""

RESPONSE=$(curl -s -X POST "https://api.github.com/user/repos" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d "$(jq -n \
    --arg name "$REPO_NAME" \
    --arg desc "$DESCRIPTION" \
    '{name: $name, description: $desc, private: false}')")

REPO_URL=$(echo "$RESPONSE" | jq -r '.html_url')
FULL_NAME=$(echo "$RESPONSE" | jq -r '.full_name')

if [ "$REPO_URL" = "null" ]; then
  echo "Error: $(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi

echo "[✓] Repository created: $REPO_URL"
echo "$FULL_NAME" > repo_full_name.txt
echo ""
echo "[*] Next step: run push_file.sh"
