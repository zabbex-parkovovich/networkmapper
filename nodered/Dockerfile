FROM nodered/node-red:latest
USER root
RUN apk update && apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir --break-system-packages paramiko
USER node-red
