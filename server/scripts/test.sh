#! /bin/sh -ex
if [ -z $CREDENTIAL_SOURCE ]
then
  ./scripts/store-secret.sh auto-id-test-secret "SECRET_KEY,SECRET_VALUE"
fi

API_ENDPOINT=$(aws cloudformation describe-stacks --region ${AWS_REGION:-ap-southeast-2} --stack-name ${AUTO_ID_STACK_NAME:-auto-id-dev} --query 'Stacks[0].Outputs[0].OutputValue' | sed -e 's/^"//' -e 's/"$//')
cd build
python3.6 crypto_client.py $API_ENDPOINT/Stage/verify ${CREDENTIAL_SOURCE:-"secretsmanager,auto-id-test-secret"}
