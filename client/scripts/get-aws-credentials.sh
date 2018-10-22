#! /bin/sh -e

export CREDENTIALS=$(python3.6 crypto_client_shell.py $AUTO_ID_API_ENDPOINT/Stage/verify "secretsmanager,$1")
aws configure set aws_access_key_id $(echo $CREDENTIALS | cut -f 1 -d ',')
aws configure set aws_secret_access_key $(echo $CREDENTIALS | cut -f 2 -d ',')

