FROM python:3.11-slim

RUN mkdir -p /opt/app && \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y npm nginx curl bash && \
    curl -sSL https://install.python-poetry.org | python3 && \
    npm install -g purgecss && \
    apt-get clean autoclean && apt-get autoremove --purge -y && npm cache clean --force
ENV PATH="/root/.local/bin:$PATH"

COPY . /opt/app/
COPY nginx.default /etc/nginx/sites-available/default

WORKDIR /opt/app
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    poetry update && \
    . "$(poetry env info --path)/bin/activate" && \
    python3 manage.py collectstatic --no-input && \
    python3 manage.py compress --force

STOPSIGNAL SIGINT
ENTRYPOINT ["./start.sh"]
