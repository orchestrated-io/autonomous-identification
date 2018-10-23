#! /bin/sh -ex

./scripts/get-keys.sh
python assumeRoleSigninUrl.py
