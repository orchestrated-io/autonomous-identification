#! /bin/sh -ex

USER_NAME=$1
SECRET_ID=$2

if [ -z $USER_NAME ] || [ -z $SECRET_ID ]
then
  echo "Usage: $0 <user_name> <secret_id>"
else
  aws secretsmanager delete-secret --region ${AWS_REGION:-ap-southeast-2} --secret-id $SECRET_ID
  aws iam delete-user-policy --user-name $USER_NAME --policy-name LimitedIAMAccess
  aws iam detach-user-policy --user-name $USER_NAME --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
  aws iam list-access-keys --user-name $USER_NAME | jq --raw-output '.AccessKeyMetadata[] | "\(.AccessKeyId)"' |
  while read -r accessKeyId
  do
    aws iam delete-access-key --user-name $USER_NAME --access-key-id $accessKeyId
  done
  aws iam delete-user --user-name $USER_NAME
fi