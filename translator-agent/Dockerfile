FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y curl gawk \
    && curl -sL https://git.io/trans -o /usr/local/bin/trans \
    && chmod +x /usr/local/bin/trans \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY skills/ /skills/

CMD ["sh", "-c", "while true; do \
    if [ -f /shutdown/terminate ]; then exit 0; fi; \
    sleep 1; \
done"]