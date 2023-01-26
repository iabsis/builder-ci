FROM ubuntu:focal
MAINTAINER olivier.b@iabsis.com
RUN mkdir /build
ENV DEBIAN_FRONTEND "noninteractive"
RUN apt update && apt -y install build-essential devscripts equivs
COPY build-dpkgbuildpackage.sh /build.sh
RUN chmod +x /build.sh
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]
