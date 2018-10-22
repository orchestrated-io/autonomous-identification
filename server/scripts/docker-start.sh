#! /bin/sh -ex
ACTION=${ACTION:-deploy}

cd /auto-id

case $ACTION in
"destroy")
  ./scripts/destroy.sh
  ;;
"test")
  ./scripts/install-sam.sh
  ./scripts/get-keys.sh
  ./scripts/test.sh
  ;;
"rotate-keys")
  ./scripts/install-keys.sh
  ;;
*)
  ./scripts/install-sam.sh
  ./scripts/deploy.sh
  ./scripts/install-keys.sh
  if [ ! -z $NPM_TOKEN ]
  then
    ./scripts/install-keys-npm.sh
  fi
  ;;
esac
