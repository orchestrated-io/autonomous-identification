import os
import boto3
from botocore.exceptions import ClientError

env = {}
aws_env = {}

aws_env['S3_BUCKET_INPUT'] = os.environ['S3_BUCKET_INPUT']
aws_env['S3_BUCKET_OUTPUT'] = os.environ['S3_BUCKET_OUTPUT']
try:
	aws_env['REGION'] = os.environ['AWS_REGION']
except:
	aws_env['REGION'] = 'ap-southeast-2'

env['INPUT_PATH'] = aws_env['S3_BUCKET_INPUT'].replace('s3://','')
env['OUTPUT_PATH'] = aws_env['S3_BUCKET_OUTPUT'].replace('s3://','')
s3_client = boto3.client('s3', region_name=aws_env['REGION'])

def input_path() -> str:
	return env['INPUT_PATH']

def output_path() -> str:
	return env['OUTPUT_PATH']

def read_s3(bucket: str, key: str) -> str:
	try:
		s3object = s3_client.get_object(Bucket=bucket, Key=key)
	except ClientError as err:
		if err.response['Error']['Code'] == 'NoSuchKey':
			raise FileNotFoundError
	except Exception as err:
		raise err
	try:
		result = s3object['Body'].read().decode('utf-8')
	except Exception as err:
		raise err
	return result

def write_s3(bucket: str, key: str, payload: str) -> None:
	try:
		s3_client.put_object(Bucket=bucket, Key=key, Body=payload)
	except ClientError as err:
		if err.response['Error']['Code'] == 'NoSuchKey':
			raise FileNotFoundError
	except Exception as err:
		raise err
	return None
