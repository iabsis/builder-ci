FROM centos:centos7
MAINTAINER olivier.b@iabsis.com
RUN mkdir /build
RUN yum -y install rpm-build make gcc
COPY build-rpmbuild.sh /build.sh
RUN chmod +x /build.sh
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]