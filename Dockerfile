FROM node:18-slim AS purgecss-builder

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git && \
    npm install -g lerna@^6.1.0 typescript ts-node pkg && \
    cd /root && git clone https://github.com/FullHuman/purgecss
WORKDIR /root/purgecss/packages/purgecss

RUN npm install && npm run build && \
    pkg . -t node18-linux-x64 --no-bytecode


FROM python:3.11-slim

RUN mkdir -p /opt/app && \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y nginx memcached curl bash && \
    curl -sSL https://install.python-poetry.org | python3 && \
    apt-get clean autoclean && apt-get autoremove --purge -y
ENV PATH="/root/.local/bin:$PATH"

COPY --from=purgecss-builder /root/purgecss/packages/purgecss/purgecss /usr/local/bin/purgecss
COPY . /opt/app/
COPY nginx.default /etc/nginx/sites-available/default

WORKDIR /opt/app
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    poetry update && \
    . "$(poetry env info --path)/bin/activate" && \
    python3 manage.py createcachetable && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py compress --force

STOPSIGNAL SIGINT
ENTRYPOINT ["./start.sh"]
