#! /bin/sh -ex

NPM_PACKAGE=${NPM_PACKAGE:-auto-id-keys}

if [ ! -z $NPM_TOKEN ]
then
	echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc
fi

sed -i'.orig' "s/@scope/@$NPM_SCOPE/g" package.json
sed -i'.orig' "s/\/package/\/$NPM_PACKAGE/g" package.json


NPM_VERSION=$(npm view @$NPM_SCOPE/$NPM_PACKAGE | grep latest | cut -d' ' -f 2)
if [ -z "$NPM_VERSION" ]
then
	NPM_VERSION=1.0.0
fi

sed -i'.orig' "s/1.0.0/$NPM_VERSION/g" package.json

mkdir -p build
./scripts/get-keys.sh
npm version patch
npm publish

mv package.json.orig package.json
rm -rf build
