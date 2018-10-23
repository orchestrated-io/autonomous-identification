#! /bin/sh -ex

if [ ! -z $NPM_TOKEN ]
then
	echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc
fi

sed -i'.orig' "s/@scope/@$NPM_SCOPE/g" package.json

NPM_VERSION=$(npm view @$NPM_SCOPE/auto-id-keys | grep latest | cut -d' ' -f 2)
sed -i'.orig' "s/1.0.0/$NPM_VERSION/g" package.json

mkdir -p build
./scripts/get-keys.sh
npm version patch
npm publish

mv package.json.orig package.json
rm -rf build
