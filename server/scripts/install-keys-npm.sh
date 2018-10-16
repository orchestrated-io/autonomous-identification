#! /bin/sh -ex


mkdir -p build
./scripts/get-keys.sh
npm version patch

sed -i'.orig' "s/@scope/@$NPM_SCOPE/g" package.json

npm publish

mv package.json.orig package.json
rm -rf build