#! /bin/sh -e

if [ -z $NPM_TOKEN ]
then
  export AWS_ACCESS_KEY_ID=$ENTROPY_ACCESS_ID
  export AWS_SECRET_ACCESS_KEY=$ENTROPY_SECRET_KEY

  aws s3 cp s3://$AUTO_ID_BUCKET/info2048.bin . 
  aws s3 cp s3://$AUTO_ID_BUCKET/public.pem .
else
  echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc
  npm install "@$NPM_SCOPE/auto-id-keys"
  cp "node_modules/@$NPM_SCOPE/auto-id-keys/build/info2048.bin" .
  cp "node_modules/@$NPM_SCOPE/auto-id-keys/build/public.pem" .
fi
