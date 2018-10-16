#! /bin/sh -ex

SECRET_EXISTS=1
aws secretsmanager get-secret-value --region ${AWS_REGION:-ap-southeast-2} --secret-id $1 || SECRET_EXISTS=0

if [ "$SECRET_EXISTS" -eq "0" ]
then
  aws secretsmanager create-secret --region ${AWS_REGION:-ap-southeast-2} --name $1 --secret-string $2
else
  aws secretsmanager put-secret-value --region ${AWS_REGION:-ap-southeast-2} --secret-id $1 --secret-string $2
fi