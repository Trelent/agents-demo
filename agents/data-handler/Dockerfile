FROM python:3.12-alpine

RUN apk add --no-cache bash libstdc++ libgcc
RUN pip install --no-cache-dir csvkit

COPY skills/ /skills/
WORKDIR /workspace

CMD ["sh", "-c", "while true; do if [ -f /shutdown/terminate ]; then exit 0; fi; sleep 1; done"]
