#! /bin/sh -ex

if [ ! -z $NPM_TOKEN ]
then
	echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc
fi

mkdir -p build
./scripts/get-keys.sh
npm version patch

sed -i'.orig' "s/@scope/@$NPM_SCOPE/g" package.json

npm publish

mv package.json.orig package.json
rm -rf build
