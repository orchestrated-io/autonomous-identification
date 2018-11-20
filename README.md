# Autonomous identification
Clients can use the autonomous identification server to obtain credentials at runtime avoiding the need to store credentials in client environments.

# Table of Contents
- [Server](#server)
	- [Overview](#overview)
	- [Try it out](#try-it-out)
		- [Using a private NPM package for the entropy file](#using-a-private-npm-package-for-the-entropy-file)
- [Storing Secrets](#storing-secrets)
- [Clients](#clients)
	- [Console client](#console-client)
	- [Auto-login client](#auto-login-client)
	- [Using the private NPM repository](#using-the-private-npm-repository)
	- [Sample Console Test Session](#sample-console-test-session)
	- [Sample Auto-login Test Session](#sample-auto-login-test-session)
- [Notes](#notes)
	- [Basic observations for secure use of this code](#basic-observations-for-secure-use-of-this-code)
	- [The verification flow](#the-verification-flow)
	- [The use of encryption](#the-use-of-encryption)
	- [Use](#use)
	- [Notes on development](#notes-on-development)

# Server
## Overview

The server runs as an AWS API endpoint retrieving secrets from AWS Secrets Manager.

## Try it out

1. [Install Docker](https://docs.docker.com/install/)
1. [Create an AWS account](https://portal.aws.amazon.com/billing/signup#/start)
1. [Configure your AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). This user should have sufficient privileges to deploy the SAM application.
1. Switch to the server directory: `cd server`
1. Build the docker image: `docker build -t auto-id .`
1. Set up an environment variable file:
	* Copy the sample file: `cp config/env.list.sample config/env.list`
	* Edit `config/env.list` and enter the correct values for each of the environment variables
	* The `NPM_TOKEN` and `NPM_SCOPE` variables can be left blank when not using a private NPM repository for the auto-id keys
1. Running the container: The basic run command is `docker run -env-file config/env.list auto-id`
	* Deploy the service: `ACTION=deploy`
	* Run a simple test: `ACTION=test`. Update `CREDENTIAL_SOURCE` if you want to use a secret name other than the default.
	* Rotate the entropy file and server key pair: `ACTION=rotate-keys`
	* Destroy the stack: `ACTION=destroy`
1. After deploy take note of the API endpoint printed to the console. This endpoint must be provided to the clients requesting credentials from the server.
1. Optionally [publish the auto-id keys to NPM](#using-a-private-npm-package-for-the-entropy-file)
1. [Store one or more secrets](#storing-secrets) in AWS Secrets Manager.
1. Use the [sample client](#client) to exercise the server

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
1. Run the container with ACTION `deploy` or `rotate-keys` with two additional parameters:
	* NPM_SCOPE - the NPM package scope
	* NPM_TOKEN - the NPM private repository token
1. The keys will be installed to S3 and to the private NPM repository

# Storing Secrets

The auto-id server deployed in the [Try it out](#try-it-out) section reads credentials from AWS Secrets Manager. After deploying the server store one or more secrets in AWS Secrets Manager as follows:

1. [Configure your AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html). This user should have sufficient privileges to deploy the SAM application.
1. Switch to the server directory: `cd server`
1. Execute the store-secret.sh script: `./scripts/store-secret.sh <SECRET_ID> <SECRET_VALUE>`

For AWS credentials store the access key ID and the secret key in a comma separated string as the SECRET_VALUE. For example: `./scripts/store-secret.sh my_test_secret "AWS_ACCESS_KEY_ID,SECRET_ACCESS_KEY"`

**NOTE: Remember to delete any secrets from Secrets Manager when done testing.**

# Clients

There are two client implementations:
1. A console client - retrieves credentials through auto-id and configured the local AWS CLI
1. An auto-login client - retrieves credentials through auto-id, assumes a role, logs into the AWS Management Console and opens a specific service page

## Console client

1. Switch to the client directory: `cd client`
1. Build the docker image: `docker build -t auto-id-client .`
1. Set up an environment variable file:
	* Copy the sample file: `cp config/env.list.sample config/env.list`
	* Edit `config/env.list` and enter the correct values for each of the environment variables
	* The `NPM_TOKEN` and `NPM_SCOPE` variables can be left blank when not using a private NPM repository for the auto-id keys
1. Running the container: The basic run command is `docker run --env-file config/env.list -ti auto-id-client /bin/sh`
	* For entropy file stored in S3 set the ENTROPY_ACCESS_ID, ENTROPY_SECRET_KEY and AUTO_ID_BUCKET environment variables
	* For entropy file stored in NPM set the NPM_TOKEN and NPM_SCOPE environment variables
1. The docker contains presents the Linux shell prompt
1. Retrieve the auto-id keys: `./scripts/get-keys.sh`
1. Retrieve the AWS credentials: `./scripts/get-aws-credentials.sh <SECRET_ID>`. Use the same secret ID used when storing the secret during server deployment. This will run `aws configure` to setup a default profile with the retrieved credentials.
1. Run aws commands to confirm the credentials have been configured correctly.

## Auto-login client

1. Switch to the client directory: `cd client`
1. Build the docker image: `docker build -t auto-id-client .`
1. Set up an environment variable file:
	* Copy the sample file: `cp config/env.list.sample config/env.list`
	* Edit `config/env.list` and enter the correct values for each of the environment variables
	* The `NPM_TOKEN` and `NPM_SCOPE` variables can be left blank when not using a private NPM repository for the auto-id keys
1. Running the container: The basic run command is `docker run --env-file config/env.list auto-id-client ./scripts/get-login-url.sh`
	* For entropy file stored in S3 set the ENTROPY_ACCESS_ID, ENTROPY_SECRET_KEY and AUTO_ID_BUCKET environment variables
	* For entropy file stored in NPM set the NPM_TOKEN and NPM_SCOPE environment variables
1. The login url script will run and return a URL that can be used in a browser to open the `VISIT_URL`

## Using the private NPM repository

If the auto-id keys have been installed to an NPM repository add the `NPM_SCOPE` and `NPM_TOKEN` environment variables when running the container. The keys will be installed from NPM.

## Sample Console Test Session

### Step 1 - Build the server docker image
```shell
autonomous-identification $ cd server
server $ docker build -t auto-id .
---->8----
```

### Step 2 - Edit the server environment variable file

Copy config/env.list.sample to config/env.list and edit config/env.list to set the correct values for each of the listed variables.

```shell
AWS_ACCESS_KEY_ID=************
AWS_SECRET_ACCESS_KEY=************
AUTO_ID_BUCKET=auto-id-test
AUTO_ID_STACK_NAME=auto-id-test

# Only change if you need to use a different secret name
CREDENTIAL_SOURCE=auto-id-test-secret

# To publish entropy file and server public key to private NPM repository
NPM_SCOPE=
NPM_TOKEN=

# ACTION is one of deploy, rotate-keys, test or destroy
ACTION=deploy
```

### Step 3 - Run the server container to deploy the server to AWS

Note that when using NPM to store keys for the client add the `NPM_TOKEN` and `NPM_SCOPE` environment variables.

```shell
server $ docker run --env-file config/env.list auto-id
---->8----
{
  "OutputKey": "APIGatewayEndpoint",
  "OutputValue": "https://**********.execute-api.ap-southeast-2.amazonaws.com",
  "Description": "API Gateway endpoint"
}
---->8----
server $ #
server $ # TAKE NOTE OF THE OutputValue above. This is the AUTO_ID_API_ENDPOINT value.
server $ #
```

### Step 4 - Store a sample secret in Secrets Manager
```shell
server $ ./scripts/store-secret.sh test-secret-id "test-secret-value1,test-secret-value2" 
---->8----
{
    "VersionId": "8f467d4a-9ecb-4262-a96e-5bec132d3bf4", 
    "Name": "test-secret-id", 
    "ARN": "arn:aws:secretsmanager:ap-southeast-2:120030542417:secret:test-secret-id-aCntKb"
}
---->8----
```

### Step 5 - Build the client docker image
```shell
server $ cd ../client
client $ docker build -t auto-id-client .
---->8----
```

### Step 6 - Edit the client environment variable file

Copy config/env.list.sample to config/env.list and edit config/env.list to set the correct values for each of the listed variables.

```shell
AUTO_ID_API_ENDPOINT=<Enter the auto id noted in step 3 here>
  
# For auto-login
ASSUME_ROLE_ARN=
ASSUME_ROLE_SESSION_NAME=
VISIT_URL=
AUTO_ID_SECRET_NAME=

# For entropy file stored in NPM
NPM_TOKEN=
NPM_SCOPE=

# For entropy file stored in S3
ENTROPY_ACCESS_ID=
ENTROPY_SECRET_KEY=
AUTO_ID_BUCKET=
```

### Step 7 - Run the client container in interactive mode

Note that when using NPM to store keys for the client add the `NPM_TOKEN` and `NPM_SCOPE` environment variables.

```shell
client $ docker run -ti --env-file config/env.list auto-id-client /bin/sh
```

### Step 8 - Retrieve the auto-id entropy file and server public key
```shell
/auto-id-client # ./scripts/get-keys.sh
download: s3://auto-id-public-repo-test/info2048.bin to ./info2048.bin
download: s3://auto-id-public-repo-test/public.pem to ./public.pem
```

### Step 9 - Request credentials from the auto-id server
```shell
/auto-id-client # ./scripts/get-aws-credentials.sh test-secret-id
```

### Step 10 - Show a profile has been configured
```shell
/auto-id-client # cat ~/.aws/credentials 
[default]
aws_access_key_id = test-secret-value1
aws_secret_access_key = test-secret-value2
/auto-id-client #
/auto-id-client # # Given valid AWS credentials you could now run AWS CLI commands sucessfully.
/auto-id-client #
/auto-id-client # exit
```

### Step 11 - Destroy the server stack
```shell
client $ cd ../server
server $ # edit config/env.list and set ACTION=destroy
server $ docker run --env-file config/env.list auto-id
server $ #
server $ # Don't forget to delete any secrets you are not going to be using from Secrets Manager.
server $ #
```


## Sample Auto-login Test Session

Follow steps 1 to 4 in the sample console session above then run the client.

### Step 1 - Edit the environment variables file

Copy config/env.list.sample to config/env.list and edit config/env.list to set the correct values for each of the listed variables.

```shell
AUTO_ID_API_ENDPOINT=https://********.execute-api.ap-southeast-2.amazonaws.com

# For auto-login
ASSUME_ROLE_ARN=arn:aws:iam::********:role/********
ASSUME_ROLE_SESSION_NAME=SampleSession
VISIT_URL=https://ap-southeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-southeast-2#dashboards:name=SomeDashboardName
AUTO_ID_SECRET_NAME=********

# For entropy file stored in NPM
NPM_TOKEN=
NPM_SCOPE=

# For entropy file stored in S3
ENTROPY_ACCESS_ID=
ENTROPY_SECRET_KEY=
AUTO_ID_BUCKET=
```

### Step 2 - Run the client to get a login URL

The sample step assumes auto-id keys are stored in an NPM repository. Use the AUTO_ID_BUCKET and AWS_* environment variables to use the keys stored in S3.

```shell
client $ docker run --env-file config/env.list auto-id-client ./scripts/get-login-url.sh
+ ./scripts/get-keys.sh
npm notice created a lockfile as package-lock.json. You should commit this file.
+ @orchestrated-io/auto-id-keys@1.0.11
added 1 package in 4.943s
+ python assumeRoleSigninUrl.py
https://signin.aws.amazon.com/federation?Action=login&Issuer=Example.org&Destination=https%3A%2F%2Fap-southeast-2.console.aws.amazon.com%2Fcloudwatch%2Fhome%3Fregion%3Dap-southeast-2%23dashboards%3Aname%3DSomeDashboardName%2F&SigninToken=***-D3ODO_GVGCSspDki8mNBeQLE7ZNw8kNLSXu4XKVEHdRP99rRXPOfsju0JfdGQyAmB9c4PK9t2M74gFbzWlo_nVS7CaQKv-mfuI_kIj44yzJA9BajPLW-hLJ1gB7EO4U4lX0pm7OMqoPyxH2-770g0U7CNcxv-_DIIh1_2R2TFc5-bj0KXdELAZkubW0SW5fl1p5lQt32RxQP3ESfev5Gjcj0ZXzRELYq4I1P2rV1uRlv8xoUO1knIgt_3mLSt43Ixdj0NJUk_duRuQE28ZjwSi8PJcvpWo3G56SLLt6FsqYTpSXdjjFbg42ssLQgxbHvjwxtk5zBieotcND313k0ABKXPnDFe1tg4gvE3UdgCJYMarH1oyJFqVZsh7k8LUVpOkXYKL6ljY0SyfOp19ZzFMcINSO4dKInaCLtT0r5Rz444Ak0pJB5nHyXse87dpdNhuudneeyXEIUjAFRpZbRzjBjpL9mwK5MQAnZaWXhr2bqIqjV1Yib_o0Uo2g_xvMnJuHUhec5dQ1k-54ivR863k9V9xZ55-eIV70QtgGcenmHA63X1xMKGhQzoqbyuBUcM1xS34ik4raeoc0I4wob2GaW6a8HeiWyNTS3LkS50uqhAnZjQDdCl7IlOslQdcr7_gQrZFBLQ7FXQReJd2SaTEWbD_Nzb5yTKqhtrVh_dS1IYG4OSh7LXCjMYCNcAeZnPbZaD29tj8qFEq7zxbn5dWqUlwde5CmAQRdljktZo8XYbmG_uPB7OHoKT_uPl0WlMDSwEd-NjuU0OIY32XsBWD2ms-uDn2Z6NeNCMyH8-qp2obLI1QgQv0Ch50Op4INyX72xbtvlSKgZcccbYZ****
client $
client $ # Copy and paste the URL above into a browser to open the management console
client $
```

# Notes

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
1. In the first exchange, the client creates the AES key and sends it (encrypted with the server's public key) to the server
2. The server sends confirmation of receipt to the client using the AES key to encrypt its response
3. The client sends the payload to the server, encrypted solely using AES
4. The server responds to the client with AES-encrypted credentials

The AES key used is randomly generated by the client every time the code is used (but not re-generated with every exchange during an existing verification session). The encryption classes included in the repo should not be altered without substantial testing afterwards. The code is unlikely to work properly on python 2.x without further work.

## Use
The `crypto_server.py` file is designed to be used as a lambda function, but can easily be adapted to a stand-alone script. The `template.yml` file is an AWS sam cli file for testing and deploying the lambda with an API gateway.

To test the lambda locally using sam cli, the local lambda and API gateway emulator is started with `sam local start-api`, which uses the aforementioned template file.

More information about aws-sam-cli is available here: https://github.com/awslabs/aws-sam-cli

## Notes on development
The version of python used for development should be 3.6 to avoid any unexpected incompatibility issues. This is also the same version used by AWS for lambda functions. For this reason, versions greater than 3.6 should be avoided at this time.

The cryptographic library used is Pycryptodome, version 3.6.6. 

