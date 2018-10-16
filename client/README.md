# Autonomous identification demonstration client
This 

# Table of Contents
- [Try it out](#try-it-out)
	- [Set up an IAM user with credentials](#set-up-an-iam-user-with-credentials)
	- [Set up auto-id key access](#set-up-auto-id-key-access)
- [Demonstration steps](#demonstration-steps)
	- [Developer console](#developer-console)
	- [CircleCI build job](#circleci-build-job)
- [Tear down](#tear-down)

## Try it out

1. [Fork the repo](https://help.github.com/articles/fork-a-repo/)
1. [Signup to CircleCI](https://circleci.com/signup/)
1. [Deploy the auto-id service](https://github.com/orchestrated-io/auto-id)
1. [Set up the IAM user](#set-up-an-iam-user-with-credentials) CircleCI will use to deploy the application.
1. [Set up auto-id key access](#set-up-auto-id-key-access)
1. Update the environment variables in [CircleCI config](.circleci/config.yml).
	* `AUTO_ID_API_ENDPOINT` must be set to the output from the auto-id service deployment.
	* `SECRET_ID` must be set to the secxret ID used when creating the IAM user
	* `AUTO_ID_BUCKET` must be set to the name of the bucket iused when deploying the auto-id server
	* `AUTO_ID_DEMO_CLIENT_BUCKET` must be set to any unqiue name for an S3 bucket. It will be created if it does not already exist.
	* `AUTO_ID_DEMO_STACK_NAME` must be set to the name of the CloudFormation stack for the demo client
1. Push the changes to your repo and monitor the build in CircleCI console
1. When the build completes the SAM CLI Hello World app is deployed. Fiund the API end point in the API Gateway console and use your browser to test the app

### Set up an IAM user with credentials

CircleCI must have AWS credentials to successfully deploy the SAM application to AWS.

Before pushing changes and triggering the CircleCI build an IAM user must be created with an access key and the access key must be stored in Secrets Manager.

To set up the user and store the access key run: `./scripts/create-iam-user.sh <user_name> <secret_id>`.

*This script requires `jq` to be installed.*

The script will:
1. Create an IAM user with the provided user name
1. Attach the PowerUserAccess managed IAM policy to the user
1. Create an inline policy for limited IAM access required by the SAM CLI deployment process ([see policy file](./scripts/limited-iam-access-policy.json))
1. Create an access key for the user
1. Store the access key id and secret access key in Secrets Manager using the provided secret ID.

### Set up auto-id key access

When CircleCI requests credentials from the auto-id service it must have access to the auto-id entropy file and public key.

There are two ways to store the auto-id keys and access must be configured accordingly.

#### Keys published as an NPM package

If the keys have been published as an NPM package the NPM scope and token must be configured in CircleCI as follows:
1. Configure the following context environment variables in CircleCI:
	* `NPM_SCOPE` is the NPM scope used when publishing the keys
	* `NPM_TOKEN` is the NPM token for access to the private repository

#### Keys stored in S3

The auto-id service itself retrieves the keys from S3 so the keys are always stored in S3.

If the client must use the keys from S3 the following process is recommended:

1. Create a new IAM user with strictly limited access. The use should have access only to read the entropy file and the auto-id server public key in the S3 bucket.
1. Create an access key for the user
1. Configure the access key id and secret into CircleCI context environment variables as follows:
	* `ENTROPY_ACCESS_ID` is the access key id
  * `ENTROPY_SECRET_KEY` is the secret access key

## Demonstration steps

There are two demonstrations:

### Developer console

1. Create an IAM user with access key stored in Secrets Manager: `./scripts/create-iam-user.sh <USER_NAME> <SECRET_NAME>`
1. Run the docker container with an interactive shell: `docker run -e NPM_SCOPE=<NPM_SCOPE> -e NPM_TOKEN=<NPM_TOKEN> -e AUTO_ID_API_ENDPOINT=<API_ENDPOINT> -ti --entrypoint /bin/sh auto-id-demo-client`
1. Run the demo script in test mode. This is done before fetching entropy file and public key to show failure: `./scripts/demo.sh test`
1. Fetch the entropy file and public key: `./scripts/get-keys.sh`
1. Run the demo script in test mode again. Service will return `SECRET_KEY,SECRET_VALUE`
1. Attempt an AWS command to show no access to AWS: `aws s3 ls`
1. Run the demo script to fetch the IAM user access credentials: `./scripts/demo.sh demo <SECRET_NAME>`
1. Attempt an AWS command to show access to AWS: `aws s3 ls`

## Tear down

To destroy the demo client stack execute the destroy script: `AUTO_ID_DEMO_CLIENT_BUCKET=<AUTO_ID_DEMO_CLIENT_BUCKET_NAME> ./scripts/destroy.sh`. The bucket name must match the name set in the CircleCI config file.
To remove the IAM user: `./scripts/delete-iam-user.sh <user_name> <secret_id>`.
