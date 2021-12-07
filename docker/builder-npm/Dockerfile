FROM debian:10

## Install Basics
RUN apt update && apt -y install curl unzip build-essential jq

## Install NodeJS
RUN curl --silent --location https://deb.nodesource.com/setup_14.x | bash -
RUN apt -y install nodejs

## Add build command
COPY build-npm.sh /build.sh
RUN chmod +x /build.sh

## Builder command
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]
