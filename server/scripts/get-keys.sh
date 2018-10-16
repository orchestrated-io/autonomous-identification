#! /bin/sh -ex

aws s3 cp s3://$AUTO_ID_BUCKET/info2048.bin build 
aws s3 cp s3://$AUTO_ID_BUCKET/public.pem build 
