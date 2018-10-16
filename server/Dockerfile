FROM ubuntu:16.04

RUN apt-get update &&  apt-get install -y software-properties-common \
    python-software-properties
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y wget ca-certificates \
    git curl vim python3.6-dev python3.6 apt-transport-https \
    build-essential openssh-client jq

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN npm install npm --global

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.6 get-pip.py
RUN pip3.6 install --upgrade pip
RUN pip install --upgrade pip
ENV PATH="/root/.local/bin:${PATH}"

COPY . /auto-id
WORKDIR /auto-id
RUN pip3.6 install -r requirements.txt

RUN pip3.6 install awscli --upgrade --user

RUN pip3.6 install aws-sam-cli --user
ENV PATH="${PATH}:/root/.local/bin"
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD /auto-id/scripts/docker-start.sh
