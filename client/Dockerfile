FROM python:3.6.6-alpine3.8

COPY . /auto-id-client

WORKDIR /auto-id-client

RUN apk update
RUN apk add bash build-base npm

RUN pip install --upgrade pip
ENV PATH="/root/.local/bin:${PATH}"

RUN pip install -r requirements.txt --user

RUN pip install awscli --upgrade --user
RUN pip install aws-sam-cli --user
ENV PATH="/root/.local/bin:${PATH}"
