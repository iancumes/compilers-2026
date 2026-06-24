#!/bin/bash
set -e

PROJECT="${GCP_PROJECT:-YOUR_PROJECT_ID}"
ZONE="${GCP_ZONE:-us-central1-a}"

if [ ! -f instance_name.txt ]; then
  echo "Error: instance_name.txt not found. Run create_instance.sh first."
  exit 1
fi

INSTANCE_NAME=$(cat instance_name.txt)

echo "[*] Authenticating with service account credentials..."
gcloud auth activate-service-account --key-file=/credentials.json --quiet
gcloud config set project "$PROJECT" --quiet

echo "[*] Deleting instance '$INSTANCE_NAME' via GCP Compute Engine API..."
gcloud compute instances delete "$INSTANCE_NAME" \
  --zone="$ZONE" \
  --quiet

echo "[✓] Instance '$INSTANCE_NAME' deleted."
rm -f instance_name.txt
