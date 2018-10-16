#! /bin/sh

USER_NAME=$1
SECRET_ID=$2
SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"

if [ -z $USER_NAME ] || [ -z $SECRET_ID ]
then
  echo "Usage: $0 <user_name> <secret_id>"
else
  aws iam create-user --user-name $USER_NAME
  if [ "$?" -eq "0" ]
  then
    aws iam attach-user-policy --user-name $USER_NAME --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
    aws iam put-user-policy --user-name $USER_NAME --policy-name LimitedIAMAccess --policy-document file://$SCRIPT_PATH/limited-iam-access-policy.json
    ACCESS_KEY=$(aws iam create-access-key --user-name $USER_NAME)
    if [ "$?" -eq "0" ]
    then
      SECRET_ACCESS_KEY=$(echo $ACCESS_KEY | jq '.AccessKey.SecretAccessKey' | tr -d '"')
      ACCESS_KEY_ID=$(echo $ACCESS_KEY | jq '.AccessKey.AccessKeyId' | tr -d '"')
      if [ -z "$ACCESS_KEY_ID" ] || [ -z "$SECRET_ACCESS_KEY"]
      then
        echo "Access key not set correctly. Please confirm AWS profile is correctly configured and there are no other errors."
      else
        ./scripts/store-secret.sh $SECRET_ID "$ACCESS_KEY_ID,$SECRET_ACCESS_KEY"
      fi
    else
      echo "Not able to create access key. Create a user with a different name or delete this user and try again." 
    fi
  else
    echo "Not able to create user. Create a user with a different name."
  fi
fi