FROM {{dist}}:{{codename}}
RUN yum -y install rpm-build make gcc yum-utils