#! /bin/sh -ex

if [ ! -d build ]
then
	mkdir build
fi

ssh-keygen -q -t rsa -N '' -f /id_rsa
./scripts/generate_entropy.sh 2048 > build/info2048.bin
cp /id_rsa build/private.pem
cp /id_rsa.pub build/public.pem

aws s3 cp build/info2048.bin s3://$AUTO_ID_BUCKET
aws s3 cp build/private.pem s3://$AUTO_ID_BUCKET
aws s3 cp build/public.pem s3://$AUTO_ID_BUCKET
