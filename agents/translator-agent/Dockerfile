FROM python:3.12-alpine

RUN apk add --no-cache bash curl gawk \
    && curl -sL https://git.io/trans -o /usr/local/bin/trans \
    && chmod +x /usr/local/bin/trans

COPY skills/ /skills/
WORKDIR /workspace

CMD ["sh", "-c", "while true; do if [ -f /shutdown/terminate ]; then exit 0; fi; sleep 1; done"]