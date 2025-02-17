#!/usr/bin/env bash

set -euo pipefail

echo "configuring sqs"
echo "==================="
AWS_REGION=eu-west-3
QUEUE_NAME=telephone-sqs

awslocal sqs create-queue --queue-name ${QUEUE_NAME} --region ${AWS_REGION} --attributes VisibilityTimeout=30
