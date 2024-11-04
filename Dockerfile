FROM {{image}}:{{tag}}
RUN apt update && apt install -y build-essential