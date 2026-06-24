#!/bin/bash
set -e

PROJECT="${GCP_PROJECT:-YOUR_PROJECT_ID}"
ZONE="${GCP_ZONE:-us-central1-a}"
INSTANCE_NAME="my-web-server"
MACHINE_TYPE="e2-micro"

echo "[*] Authenticating with service account credentials..."
gcloud auth activate-service-account --key-file=/credentials.json --quiet

echo "[*] Setting project to '$PROJECT'..."
gcloud config set project "$PROJECT" --quiet

echo ""
echo "[*] Calling the GCP Compute Engine API directly..."
echo "[*] Project:      $PROJECT"
echo "[*] Zone:         $ZONE"
echo "[*] Machine type: $MACHINE_TYPE"
echo ""

gcloud compute instances create "$INSTANCE_NAME" \
  --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --format=json | jq '{name: .name, status: .status, zone: .zone}'

echo ""
echo "[✓] Instance '$INSTANCE_NAME' created in zone $ZONE."
echo "$INSTANCE_NAME" > instance_name.txt
echo "[!] IMPORTANT: delete it when done — run delete_instance.sh"
