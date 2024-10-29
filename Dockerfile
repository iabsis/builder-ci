FROM debian
RUN apt update && apt install -y podman make ca-certificates