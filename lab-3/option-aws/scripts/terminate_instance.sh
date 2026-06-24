#!/bin/bash
set -e

export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_KEY"
export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

if [ ! -f instance_id.txt ]; then
  echo "Error: instance_id.txt not found. Run create_instance.sh first."
  exit 1
fi

INSTANCE_ID=$(cat instance_id.txt)
echo "[*] Terminating instance $INSTANCE_ID via AWS EC2 API..."

aws ec2 terminate-instances \
  --instance-ids "$INSTANCE_ID" \
  --output json | jq '.TerminatingInstances[0].CurrentState'

echo "[✓] Instance $INSTANCE_ID is being terminated."
rm -f instance_id.txt
