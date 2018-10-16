#! /bin/sh -ex
AWS_REGION=${AWS_REGION:-ap-southeast-2}

aws cloudformation delete-stack --stack-name ${AUTO_ID_STACK_NAME:-auto-id-dev} --region $AWS_REGION
aws s3 rm s3://$AUTO_ID_BUCKET --recursive --region $AWS_REGION
aws s3 rb s3://$AUTO_ID_BUCKET --region $AWS_REGION