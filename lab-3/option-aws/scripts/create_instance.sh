#!/bin/bash
set -e

export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="$AWS_SECRET_KEY"
export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

INSTANCE_NAME="my-web-server"
AMI_ID="ami-0c55b159cbfafe1f0"   # Amazon Linux 2 in us-east-1
INSTANCE_TYPE="t2.micro"

echo "[*] Calling the AWS EC2 API directly..."
echo "[*] Region:        $AWS_DEFAULT_REGION"
echo "[*] AMI:           $AMI_ID"
echo "[*] Instance type: $INSTANCE_TYPE"
echo ""

RESPONSE=$(aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --count 1 \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
  --output json)

INSTANCE_ID=$(echo "$RESPONSE" | jq -r '.Instances[0].InstanceId')
STATE=$(echo "$RESPONSE" | jq -r '.Instances[0].State.Name')

echo "[✓] EC2 instance launched!"
echo "    ID:    $INSTANCE_ID"
echo "    State: $STATE"
echo ""
echo "$INSTANCE_ID" > instance_id.txt
echo "[!] IMPORTANT: terminate it when done — run terminate_instance.sh"
