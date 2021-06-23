FROM fedora:34
MAINTAINER olivier.b@iabsis.com
RUN mkdir /build
RUN dnf -y install fedora-packager fedora-review make gcc
COPY build-rpmbuild.sh /build.sh
RUN chmod +x /build.sh
WORKDIR /build/sources
ENTRYPOINT ["/build.sh"]