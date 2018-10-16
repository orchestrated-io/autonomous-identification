# Autonomous identification
Clients can use the autonomous identification server to obtain credentials at runtime avoiding the need to store credentials in client environments.

# Table of Contents
- [Server](#server)
	- [Overview](#overview)
	- [Try it out](#try-it-out)
		- [Using a private NPM package for the entropy file](#using-a-private-npm-package-for-the-entropy-file)
	- [Basic observations for secure use of this code](#basic-observations-for-secure-use-of-this-code)
	- [The verification flow](#the-verification-flow)
	- [The use of encryption](#the-use-of-encryption)
	- [Use](#use)
	- [Notes on development](#notes-on-development)
- [Storing Secrets](#storing-secrets)
- [Client](#client)

# Server
## Overview

The server runs as an AWS API endpoint retrieving secrets from AWS Secrets Manager.

## Try it out

1. [Install Docker](https://docs.docker.com/install/)
1. [Create an AWS account](https://portal.aws.amazon.com/billing/signup#/start)
1. [Configure your AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). This user should have sufficient privileges to deploy the SAM application.
1. Switch to the server directory: `cd server`
1. Build the docker image: `docker build -t auto-id .`
1. Running the container: The basic run command is `docker run -e AWS_ACCESS_KEY_ID=<AWS_KEY_ID> -e AWS_SECRET_ACCESS_KEY=<AWS_SECRET_KEY> -e AUTO_ID_BUCKET=<ANY_UNIQUE_BUCKET_NAME> -e AUTO_ID_STACK_NAME=<ANY_UNIQUE_STACK_NAME> -e ACTION=<deploy|test|rotate-keys|destroy> auto-id`
	* Deploy the service: Omit the action parameter or set it to `deploy`.
	* Run a simple test: Set the action parameter to `test`. Add the credential store paramater to specify which secret to retrieve: `-e CREDENTIAL_SOURCE="secretsmanager,<secret_id>"`. The store name must be `secretsmanager`. The secret id can be the Secrets Manager secret ARN or the friendly secret name.
	* Rotate the entropy file and server key pair: Set the action parameter to `rotate-keys`
	* Destroy the stack: Set the action parameter to `destroy`
1. After deploy take note of the API endpoint printed to the console. This endpoint must be provided to the clients requesting credentials from the server.
1. Optionally [publish the auto-id keys to NPM](#using-a-private-npm-package-for-the-entropy-file)
1. [Store one or more secrets](#storing-secrets) in AWS Secrets Manager.
1. Use the [sample clients](#clients) to exercise the server

When deploying the service the optional arguments have the following defaults:
* ACTION: `deploy`
* STACK_NAME: `auto-id-dev`
* AWS_REGION: `ap-southeast-2`

The AWS credentials and bucket name are mandatory.

### Using a private NPM package for the entropy file

When the server is deployed the public and private RSA keys are stored in an S3 bucket along with the entropy file.

The auto-id client would require access to the S3 bucket to get the entropy file and server public key.

As an alternative the entropy file and server public key can be published as an NPM package. To do this:

1. [Setup private NPM repository](https://docs.npmjs.com/private-modules/intro)
1. Create a `.npmrc` file in the root of the project
1. Obtain the NPM token and store it in `.npmrc`: `//registry.npmjs.org/:_authToken=<NPM TOKEN>`
1. Publish the NPM package: `NPM_SCOPE=<NPM_SCOPE> AUTO_ID_BUCKET=<BUCKET_NAME> ./scripts/install-keys-npm.sh`

The `BUCKET_NAME` here must match that provided during deploy. This script will retrieve the keys from the S3 bucket and package them to be published to NPM.

## Basic observations for secure use of this code
1. The client should have access to an entropy file, which must remain secret. The client also has the public key of the server.
2. The server has a private key and an *independent* copy of the entropy file, which is used to verify that the client actually has this file.
3. The entropy file should be rotated on a regular basis. The more frequently it can be rotated, the better.
4. The keys for the server should also be rotated regularly.

## The verification flow
1. The client code is deployed to a container.
2. The client container has the code from its repository, which may include the public key of the verification server.
3. The client container has access to a remote filesystem or another code repository where the entropy file is located. The client copies that file into itself.
4. The client 
	- executes the crypto_client.py script, which generates an AES key
	- randomly selects a section of the entropy file 
	- hashes the combined selections from that file
	- creates a payload with the hash and intervals that were randomly selected to create the hash 
5. The payload is encrypted using AES and it, together with the AES key are then encrypted with the server's public key, and sent to the server.
6. The server receives the encrypted payload, decrypts it with its private key, uses the AES key it just received to decrypt the AES encrypted payload, calculates the same hash from *its own copy* of the entropy file, and compares the hashes. 
7. If the hashes match, the server sends the needed credentials to the server.

## The use of encryption
Two types of encryption are used: RSA and AES. RSA is not used exclusively, as it is limited in the size of text it can encrypt, and there is no way for the server to securely reply to the client, as the client does not have its own RSA keypair.

In the event the size of the AES encrypted payload exceeds that of what can be encrypted with RSA in the initial message sent from the client to the server, one extra exchange of data is needed between the client and the server.

The flow would be: 
	- In the first exchange, the client creates the AES key and sends it (encrypted with the server's public key) to the server
	- The server sends confirmation of receipt to the client using the AES key to encrypt its response
	- The client sends the payload to the server, encrypted solely using AES
	- The server responds to the client with AES-encrypted credentials

The AES key used is randomly generated by the client every time the code is used (but not re-generated with every exchange during an existing verification session). The encryption classes included in the repo should not be altered without substantial testing afterwards. The code is unlikely to work properly on python 2.x without further work.

## Use
The `crypto_server.py` file is designed to be used as a lambda function, but can easily be adapted to a stand-alone script. The `template.yml` file is an AWS sam cli file for testing and deploying the lambda with an API gateway.

To test the lambda locally using sam cli, the local lambda and API gateway emulator is started with `sam local start-api`, which uses the aforementioned template file.

More information about aws-sam-cli is available here: https://github.com/awslabs/aws-sam-cli

## Notes on development
The version of python used for development should be 3.6 to avoid any unexpected incompatibility issues. This is also the same version used by AWS for lambda functions. For this reason, versions greater than 3.6 should be avoided at this time.

The cryptographic library used is Pycryptodome, version 3.6.6. 

# Storing Secrets

The auto-id server deployed in the [Try it out](#try-it-out) section reads credentials from AWS Secrets Manager. After deploying the server store one or more secrets in AWS Secrets Manager as follows:

1. [Configure your AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). This user should have sufficient privileges to deploy the SAM application.
1. Switch to the server directory: `cd server`
1. Execute the store-secret.sh script: `./scripts/store-secret.sh <SECRET_ID> <SECRET_VALUE>`

For AWS credentials store the access key ID and the secret key in a comma separated string as the SECRET_VALUE. For example: `./scripts/store-secret.sh my_test_secret "AWS_ACCESS_KEY_ID,SECRET_ACCESS_KEY"`

# Client

The client is a docker container that uses auto-id to retrieve AWS credentials.

To run the console:

1. Switch to the client directory: `cd client`
1. Build the docker image: `docker build -t auto-id-client-console .`
1. Running the container: The basic run command is `docker run -e AUTO_ID_API_ENDPOINT=<the api endpoint noted in the server deployment> -ti --entrypoint /bin/sh auto-id-client-console`
	* For entropy file stored in S3 add the ENTROPY_ACCESS_ID, ENTROPY_SECRET_KEY and AUTO_ID_BUCKET environment variables: `docker run -e ENTROPY_ACCESS_ID=<AWS_KEY_ID> -e ENTROPY_SECRET_KEY=<AWS_SECRET_KEY> -e AUTO_ID_BUCKET=<THE_AUTO_ID_BUCKET_NAME> ...`
	* For entropy file stored in NPM add the NPM_TOKEN environment variable: `docker run -e NPM_TOKEN=<AWS_KEY_ID> ...`
1. The docker contains presents the Linux shell prompt
1. Retrieve the auto-id keys: `./scripts/get-keys.sh`
1. Retrieve the AWS credentials: `./scripts/get-aws-credentials.sh <SECRET_ID>`. Use the same secret ID used when storing the secret during server deployment. This will run `aws configure` to setup a default profile with the retrieved credentials.
1. Run aws commands to confirm the credentials have been configured correctly.
