FROM {{distrib}}:{{codename}}
RUN apt update && apt install -y build-essential devscripts