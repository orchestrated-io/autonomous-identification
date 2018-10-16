import os
import boto3

aws_env = {}

try:
	aws_env['REGION'] = os.environ['AWS_REGION']
except:
	aws_env['REGION'] = 'ap-southeast-2'

secrets_manager_client = boto3.client('secretsmanager', region_name=aws_env['REGION'])

def set_vars(input_array: list) -> list:
	store, ID = input_array[0:2]
	try:
		version = input_array[2]
	except:
		version = None
	try:
		stage = input_array[3]
	except:
		stage = None
	return [store, ID, version, stage]

def retrieve_credentials(credential_source: str) -> str:
	source_array = credential_source.split(',')
	if len(source_array) < 2:
		error = 'Credential source must include store name and secret id, e.g. '
		error += 'store_name,secret_id[,secret_version[,secret_stage]]'
		raise ValueError(error)

	secret_store, secret_id, secret_version, secret_stage = set_vars(source_array)

	try:
		if secret_version is not None:
			response = secrets_manager_client.get_secret_value(
				SecretId=secret_id,
				VersionId=secret_version
			)
		elif secret_stage is not None:
			response = secrets_manager_client.get_secret_value(
				SecretId=secret_id,
				VersionStage=secret_stage
			)
		else:
			response = secrets_manager_client.get_secret_value(
				SecretId=secret_id
			)
	except Exception as err:
		raise err

	try:
		result = response['SecretString']
	except Exception as err:
		raise err
	return result