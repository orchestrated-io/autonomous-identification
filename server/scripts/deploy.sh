#! /bin/sh -ex
AWS_REGION=${AWS_REGION:-ap-southeast-2}
STACK_NAME=${AUTO_ID_STACK_NAME:-auto-id-dev}

aws s3 ls | grep $AUTO_ID_BUCKET || aws s3 mb s3://$AUTO_ID_BUCKET --region=$AWS_REGION

sam package \
  --template-file template.yaml \
  --s3-bucket $AUTO_ID_BUCKET \
  --output-template-file template-packaged.yaml
sam deploy \
  --template-file template-packaged.yaml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION \
  --parameter-overrides AutoIdBucket=$AUTO_ID_BUCKET

aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --region $AWS_REGION | jq -r '.Stacks[0].Outputs[0]'