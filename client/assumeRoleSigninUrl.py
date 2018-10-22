import os, sys
import urllib, json
import requests
import boto3
import crypto_client

credentials = crypto_client.get_credentials(("").join([os.environ["AUTO_ID_API_ENDPOINT"], "/Stage/verify"]), os.environ["AUTO_ID_SECRET_NAME"])
parts = credentials.split(',')

sts_client = boto3.client('sts', aws_access_key_id=parts[0], aws_secret_access_key=parts[1])

assumed_role_object = sts_client.assume_role(
    RoleArn=os.environ["ASSUME_ROLE_ARN"],
    RoleSessionName=os.environ["ASSUME_ROLE_SESSION_NAME"]
)

credentials = {
	"sessionId":  assumed_role_object["Credentials"]["AccessKeyId"],
	"sessionKey": assumed_role_object["Credentials"]["SecretAccessKey"],
	"sessionToken": assumed_role_object["Credentials"]["SessionToken"]
}

json_string_with_temp_credentials = json.dumps(credentials)

request_parameters = "?Action=getSigninToken"
request_parameters += "&SessionDuration=43200"
request_parameters += "&Session=" + urllib.parse.quote_plus(json_string_with_temp_credentials)
request_url = "https://signin.aws.amazon.com/federation" + request_parameters
r = requests.get(request_url)

signin_token = json.loads(r.text)

request_parameters = "?Action=login" 
request_parameters += "&Issuer=Example.org" 
request_parameters += "&Destination=" + urllib.parse.quote_plus(os.environ["VISIT_URL"])
request_parameters += "&SigninToken=" + signin_token["SigninToken"]
request_url = "https://signin.aws.amazon.com/federation" + request_parameters

print(request_url)
